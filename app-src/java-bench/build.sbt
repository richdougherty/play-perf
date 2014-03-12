name := "java-bench"

version := "1.0-SNAPSHOT"

libraryDependencies ++= Seq(
  javaJdbc,
  javaEbean,
  javaWs,
  cache,
  json
)

javacOptions ++= Seq("-Xlint:deprecation")

play.Project.playJavaSettings
