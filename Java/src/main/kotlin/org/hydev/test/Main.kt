package org.hydev.test

import com.github.doyaaaaaken.kotlincsv.dsl.csvReader
import com.google.gson.GsonBuilder
import org.apache.lucene.analysis.standard.StandardAnalyzer
import org.apache.lucene.document.Document
import org.apache.lucene.document.Field
import org.apache.lucene.document.IntPoint
import org.apache.lucene.document.TextField
import org.apache.lucene.index.DirectoryReader
import org.apache.lucene.index.IndexWriter
import org.apache.lucene.index.IndexWriterConfig
import org.apache.lucene.search.BooleanClause.Occur
import org.apache.lucene.search.BooleanQuery
import org.apache.lucene.search.BoostQuery
import org.apache.lucene.search.IndexSearcher
import org.apache.lucene.search.ScoreDoc
import org.apache.lucene.search.similarities.ClassicSimilarity
import org.apache.lucene.store.FSDirectory
import org.apache.lucene.util.QueryBuilder
import java.nio.file.Path
import kotlin.io.path.isDirectory
import kotlin.io.path.readText
import kotlin.io.path.writeText


lateinit var BASEDIR: Path
lateinit var INDEX_DIR: Path
lateinit var OUTPUT_DIR: Path
lateinit var SRC_DIR: Path
val ANALYZER = StandardAnalyzer()

const val TYPE_REVIEW = 1
const val TYPE_FILE = 2

/**
 * Get structure category of a file
 *
 * 0: UI
 * 1: Android Manifest
 * 2: Content Provider
 * 3: Service
 * -1: Other
 */
fun structureCategorySrc(content: str, path: Path): Int
{
    val c = content.lowercase()
    val p = path.toString()

    return if (listOf("/res/", "/resources/", "/ui", "Activity").any { it in p }) 0
        else if ("AndroidManifest" in p) 1
        else if (listOf("content", "provider").any { it in c }) 2
        else if ("service" in p) 3
        else -1
}

fun structureCategoryReview(review: dict<str, str>): Int
{
    return if (review["IS_UI"] == "1") 0
        else if (review["IS_COMPATIBILITY"] == "1" || review["IS_PRIVACY"] == "1") 1
        else if (review["preclasses"]?.contains("RESOURCES") == true) 2
        else -1
}

/**
 * Create document and index it
 */
fun IndexWriter.indexFile(path: Path)
{
    val content = path.readText()
    val sc = structureCategorySrc(content, path)

    addDocument(Document().apply {
        add(TextField("path", "File $path", Field.Store.YES))
        add(TextField("text", content, Field.Store.YES))
        if (sc != -1) add(IntPoint("structure_category", sc))
        add(IntPoint("type", TYPE_FILE))
    })
}

//fun IndexWriter.indexReview(review: dict<str, str>)
//{
//    addDocument(Document().apply {
//        add(TextField("path", "Review ${review["_id"]}", Field.Store.YES))
//        add(TextField("text", review["reviewTextProc"], Field.Store.YES))
//        add(IntPoint("type", TYPE_REVIEW))
//    })
//}

/**
 * Open app directory, and index app if not already indexed
 */
fun <T> withApp(pkg: str, callback: (Path, FSDirectory, DirectoryReader) -> T): T
{
    val dp = SRC_DIR / pkg
    val ip = INDEX_DIR / pkg
    FSDirectory.open(ip).use { dir ->
        // Not already indexed
        if (!ip.isDirectory() || ip.toFile().list()?.isEmpty() == true)
            indexApp(pkg, dp, dir)

        // Create reader
        DirectoryReader.open(dir).use { reader ->
            return callback(dp, dir, reader)
        }
    }
}

fun reviews(pkg: str): List<Map<String, String>>
{
    return csvReader().readAllWithHeader((BASEDIR / "reviews.processed.csv").toFile()).filter { it["pkg"] == pkg }
}

/**
 * Index one app
 */
fun indexApp(pkg: str, path: Path, dir: FSDirectory)
{
    println("Indexing $pkg...")

    // Create index writer
    IndexWriter(dir, IndexWriterConfig(ANALYZER)).use { writer ->
        // Loop through all processed java and xml files
        path.toFile().walk().filter { str(it).endsWith(".java.proc.txt") }.forEach { writer.indexFile(it.toPath()) }

        // Loop through all processed reviews
//        reviews(pkg).forEach { writer.indexReview(it) }
    }
}

/**
 * Search for a review
 */
fun IndexSearcher.searchReview(txt: str, sc: Int? = null, n: Int = 10, fileOnly: Boolean = false): Array<out ScoreDoc>
{
    if (txt.isBlank()) return emptyArray()
    val sc1 = if (sc == -1) null else sc

    // Create query
    val query = BooleanQuery.Builder().apply {
        add(QueryBuilder(ANALYZER).createMinShouldMatchQuery("text", txt, 0.2f), Occur.MUST)
        sc1?.let { add(BoostQuery(IntPoint.newExactQuery("structure_category", sc1), 0.3f), Occur.SHOULD) }
        if (fileOnly) add(IntPoint.newExactQuery("type", TYPE_FILE), Occur.MUST)
    }.build()

//    val analyzer = StandardAnalyzer()
//    val tokenStream: TokenStream = analyzer.tokenStream("Fieldname", txt)
//    val termAttribute = tokenStream.getAttribute(CharTermAttribute::class.java)
//
//    val bq = BooleanQuery.Builder()
//    tokenStream.reset()
//    while (tokenStream.incrementToken()) bq.add(TermQuery(Term("text", termAttribute.toString())), Occur.SHOULD)
//    tokenStream.close()
//
//    // defines IndexCategory and integrate to search
//    sc1?.let { bq.add(BoostQuery(IntPoint.newExactQuery("structure_category", sc1), 0.3f), Occur.SHOULD) }
//
//    val query = bq.build()

    // Search query
    return search(query, n).scoreDocs
}

fun processApp(pkg: str)
{
    // Index app if not already
    withApp(pkg) { path, dir, reader ->
        // Create searcher
        val searcher = IndexSearcher(reader).apply { similarity = ClassicSimilarity() }

        println("Searching $path...")

        val hitsStats = arrayListOf<Int>()

        // Loop through each review
        val reviews = reviews(pkg).map { review ->
            // Search for the review
            val sc = structureCategoryReview(review)
            val hits = searcher.searchReview(review["reviewTextProc"]!!, sc, fileOnly = true)

            println("Review ${review["_id"]} found ${hits.size} hits")
//            hits.forEach {
//                val doc = searcher.doc(it.doc)
//                println("Hit! #${it.doc} Score ${it.score} - ${doc["path"]}")
//            }
            hitsStats.add(hits.size)

            // Store files in json
            val files = hits.map { mapOf("path" to searcher.doc(it.doc)["path"].substringAfter("$pkg/"), "score" to it.score) }
            val r: MutableMap<str, Any> = review
                .filterKeys { it in listOf("_id", "reviewText", "reviewTextProc", "ratingStars", "preclasses", "subclasses") }
                .toMutableMap()
            r["source"] = files
            r
        }

        println("Average number of hits: ${hitsStats.toIntArray().average()}")

        // Store JSON
        (OUTPUT_DIR / "$pkg.json").apply {
            parent.toFile().mkdirs()
            writeText(GsonBuilder().setPrettyPrinting().create().toJson(reviews))
        }
    }
}

fun main(args: Array<String>)
{
    if (args.isEmpty()) return println("Usage: java <p3.jar> <RQ2 Path>")

    BASEDIR = Path(args[0])
    INDEX_DIR = BASEDIR / "Lucene" / "Index"
    OUTPUT_DIR = BASEDIR / "Lucene" / "Results"
    SRC_DIR = BASEDIR / "Source"

    val apps = SRC_DIR.toFile().list()?.toList()
    if (apps == null || apps.isEmpty()) return println("Error: No apps found under $SRC_DIR")

    apps.forEach(::processApp)
}
