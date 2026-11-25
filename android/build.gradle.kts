plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}

tasks.register("validateProductionApiUrl") {
    doLast {
        val apiUrl = providers.gradleProperty("DHANRAJ_API_BASE_URL").orNull.orEmpty()
        require(apiUrl.startsWith("https://") && apiUrl.endsWith("/")) {
            "Set -PDHANRAJ_API_BASE_URL=https://your-api-host/ to build a production APK."
        }
    }
}

tasks.configureEach {
    if ((name.startsWith("assemble") || name.startsWith("bundle")) && name.contains("Release")) {
        dependsOn("validateProductionApiUrl")
    }
}