package com.emochi.app.data  
  
import android.content.Context  
import com.emochi.app.model.ChatMessage  
import kotlinx.serialization.Serializable  
import kotlinx.serialization.json.Json  
import kotlinx.serialization.encodeToString  
import kotlinx.serialization.decodeFromString  
import java.io.File  
  
class LocalStore(private val context: Context) {  
    private val json = Json { ignoreUnknownKeys = true; prettyPrint = true }  
    private val storageDir = File(context.filesDir, "chats")  
      
    init { if (!storageDir.exists()) storageDir.mkdirs() }  
      
    fun saveChat(chatId: String, messages: List<ChatMessage>) {  
        try {  
            val file = File(storageDir, "$chatId.json")  
            val serializable = messages.map { SerializableChatMessage.from(it) }  
            file.writeText(json.encodeToString(serializable))  
        } catch (e: Exception) { e.printStackTrace() }  
    }  
      
    fun loadChat(chatId: String): List<ChatMessage>? {  
        return try {  
            val file = File(storageDir, "$chatId.json")  
            if (!file.exists()) return null  
            val serializable: List<SerializableChatMessage> = json.decodeFromString(file.readText())  
            serializable.map { it.toChatMessage() }  
        } catch (e: Exception) { e.printStackTrace(); null }  
    }  
}  
  
@Serializable  
data class SerializableChatMessage(val id: String, val role: String, val content: String, val timestamp: Long) {  
    fun toChatMessage() = ChatMessage(id = id, role = role, content = content, timestamp = timestamp)  
    companion object {  
        fun from(msg: ChatMessage) = SerializableChatMessage(id = msg.id, role = msg.role, content = msg.content, timestamp = msg.timestamp)  
    }  
}