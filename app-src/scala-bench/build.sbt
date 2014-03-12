name := "scala-bench"

version := "1.0-SNAPSHOT"

libraryDependencies ++= Seq(
  jdbc,
  anorm,
  cache,
  ws,
  json
)     

play.Project.playScalaSettings
