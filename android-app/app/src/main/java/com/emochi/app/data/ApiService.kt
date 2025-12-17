package com.emochi.app.data  
  
import com.emochi.app.model.*  
import io.ktor.client.*  
import io.ktor.client.call.*  
import io.ktor.client.engine.okhttp.*  
import io.ktor.client.request.*  
import io.ktor.client.plugins.contentnegotiation.*  
import io.ktor.serialization.kotlinx.json.*  
import io.ktor.http.*  
import kotlinx.serialization.json.Json  
import android.util.Log  
  
class ApiService(private val baseUrl: String = "http://10.0.2.2:8001") {  
    private val client = HttpClient(OkHttp) {  
        install(ContentNegotiation) {  
            json(Json { ignoreUnknownKeys = true; isLenient = true })  
        }  
        engine {  
            config {  
                connectTimeout(60, java.util.concurrent.TimeUnit.SECONDS)  
                readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)  
            }  
        }  
    }  
      
    suspend fun sendMessage(chatId: String, text: String, provider: String? = null, modelHint: String? = null): MessageResponse {  
        return try {  
            val response = client.post("$baseUrl/chat/$chatId/message") {  
                contentType(ContentType.Application.Json)  
                setBody(MessageRequest(text = text, provider = provider, model_hint = modelHint))  
            }  
            response.body()  
        } catch (e: Exception) {  
            Log.e("ApiService", "Error sending message", e)  
            throw e  
        }  
    }  
      
    suspend fun setModel(chatId: String, model: String): Boolean {  
        return try {  
            client.post("$baseUrl/chat/$chatId/model") {  
                contentType(ContentType.Application.Json)  
                setBody(ModelRequest(model = model))  
            }  
            true  
        } catch (e: Exception) {  
            Log.e("ApiService", "Error setting model", e)  
            false  
        }  
    }  
      
    suspend fun setSettings(chatId: String, intro: String? = null, personality: String? = null, welcome: String? = null, tags: List<String>? = null, gender: String? = null): Boolean {  
        return try {  
            client.post("$baseUrl/chat/$chatId/settings") {  
                contentType(ContentType.Application.Json)  
                setBody(SettingsRequest(intro = intro, personality = personality, welcome = welcome, tags = tags, gender = gender))  
            }  
            true  
        } catch (e: Exception) {  
            Log.e("ApiService", "Error setting settings", e)  
            false  
        }  
    }  
      
    fun close() { client.close() }  
}