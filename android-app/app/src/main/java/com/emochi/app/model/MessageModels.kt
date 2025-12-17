package com.emochi.app.model  
  
import kotlinx.serialization.Serializable  
  
@Serializable  
data class MessageRequest(val text: String, val provider: String? = null, val model_hint: String? = null)  
  
@Serializable  
data class MessageResponse(val chat_id: String, val model: String, val reply: String, val emotion_hint: EmotionHint? = null)  
  
@Serializable  
data class EmotionHint(val primary: String? = null, val intensity: Int = 0, val meta: MetaStats? = null, val snippet: String? = null, val contradiction: Boolean = false)  
  
@Serializable  
data class MetaStats(val attraction: Int = 0, val trust: Int = 0, val anger: Int = 0)  
  
data class ChatMessage(val id: String, val role: String, val content: String, val timestamp: Long = System.currentTimeMillis(), val emotionHint: EmotionHint? = null)  
  
@Serializable  
data class ModelRequest(val model: String)  
  
@Serializable  
data class SettingsRequest(val intro: String? = null, val personality: String? = null, val welcome: String? = null, val tags: List<String>? = null, val gender: String? = null)  
  
val PERSONALITY_MODELS = listOf("Vanilla", "Vanilla Short", "Matcha", "Strawberry", "Chocolate", "Peach", "Mint", "Blueberry", "Blackberry", "Rainbow", "Unicorn", "Sage")  
  
val BEHAVIOR_TAGS = listOf("Flirty", "Romantic", "Dominant", "Submissive", "Seductive", "Taboo", "Dark Romance", "Tsundere", "Yandere", "Bratty", "Demon", "Cold")