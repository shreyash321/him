package com.dhanraj.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.view.WindowCompat
import androidx.lifecycle.ViewModelProvider
import com.dhanraj.app.data.remote.ApiFactory
import com.dhanraj.app.data.repository.DhanRajRepository
import com.dhanraj.app.ui.DhanRajApp
import com.dhanraj.app.viewmodel.AppViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        WindowCompat.getInsetsController(window, window.decorView).isAppearanceLightStatusBars = true
        WindowCompat.getInsetsController(window, window.decorView).isAppearanceLightNavigationBars = true

        val client = ApiFactory.create(applicationContext)
        val repository = DhanRajRepository(client.api)
        val factory = AppViewModel.factory(repository, client.cookies)
        val viewModel = ViewModelProvider(this, factory)[AppViewModel::class.java]

        setContent {
            DhanRajApp(viewModel = viewModel)
        }
    }
}
