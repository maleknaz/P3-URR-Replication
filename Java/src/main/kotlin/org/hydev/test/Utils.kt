package org.hydev.test

import java.nio.file.Path
import java.nio.file.Paths


// Join paths with division symbol
operator fun Path.div(next: String): Path = Paths.get(this.toString(), next)

// Create paths with constructor
fun Path(path: String, vararg paths: String): Path = Paths.get(path, *paths)

// Python syntax
typealias str = String
typealias dict<A, B> = Map<A, B>
fun str(o: Any) = o.toString()
