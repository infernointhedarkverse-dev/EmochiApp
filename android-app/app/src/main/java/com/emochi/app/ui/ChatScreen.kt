package com.emochi.app.ui  
  
import androidx.compose.foundation.layout.*  
import androidx.compose.foundation.lazy.LazyColumn  
import androidx.compose.foundation.lazy.items  
import androidx.compose.foundation.lazy.rememberLazyListState  
import androidx.compose.foundation.shape.RoundedCornerShape  
import androidx.compose.material.icons.Icons  
import androidx.compose.material.icons.filled.Send  
import androidx.compose.material.icons.filled.Settings  
import androidx.compose.material3.*  
import androidx.compose.runtime.*  
import androidx.compose.ui.Alignment  
import androidx.compose.ui.Modifier  
import androidx.compose.ui.platform.LocalContext  
import androidx.compose.ui.text.font.FontWeight  
import androidx.compose.ui.unit.dp  
import androidx.compose.ui.unit.sp  
import com.emochi.app.data.ApiService  
import com.emochi.app.data.LocalStore  
import com.emochi.app.model.ChatMessage  
import kotlinx.coroutines.launch  
import java.util.UUID  
  
@OptIn(ExperimentalMaterial3Api::class)  
@Composable  
fun ChatScreen() {  
    val context = LocalContext.current  
    val apiService = remember { ApiService() }  
    val localStore = remember { LocalStore(context) }  
    val chatId = "default_chat"  
    val scope = rememberCoroutineScope()  
    val listState = rememberLazyListState()  
    var messages by remember { mutableStateOf<List<ChatMessage>>(emptyList()) }  
    var inputText by remember { mutableStateOf("") }  
    var isLoading by remember { mutableStateOf(false) }  
    var showSettings by remember { mutableStateOf(false) }  
    var showModelSelector by remember { mutableStateOf(false) }  
    var currentModel by remember { mutableStateOf("Vanilla") }  
    var errorMessage by remember { mutableStateOf<String?>(null) }  
      
    LaunchedEffect(Unit) { localStore.loadChat(chatId)?.let { messages = it } }  
    LaunchedEffect(messages.size) { if (messages.isNotEmpty()) listState.animateScrollToItem(messages.size - 1) }  
      
    Scaffold(topBar = {  
        TopAppBar(title = { Column { Text("Emochi Chat", fontWeight = FontWeight.Bold); Text("Model: $currentModel", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)) } },  
            actions = { IconButton(onClick = { showModelSelector = true }) { Text("🎭", fontSize = 24.sp) }; IconButton(onClick = { showSettings = true }) { Icon(Icons.Default.Settings, contentDescription = "Settings") } })  
    }) { paddingValues ->  
        Column(modifier = Modifier.fillMaxSize().padding(paddingValues)) {  
            errorMessage?.let { error -> Surface(modifier = Modifier.fillMaxWidth(), color = MaterialTheme.colorScheme.errorContainer) { Text(error, modifier = Modifier.padding(8.dp), color = MaterialTheme.colorScheme.onErrorContainer) } }  
            LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth(), state = listState, contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {  
                items(messages) { message -> MessageBubble(message) }  
                if (isLoading) item { Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Start) { CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp); Spacer(modifier = Modifier.width(8.dp)); Text("Thinking...", color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)) } }  
            }  
            Surface(modifier = Modifier.fillMaxWidth(), shadowElevation = 8.dp) {  
                Row(modifier = Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {  
                    OutlinedTextField(value = inputText, onValueChange = { inputText = it }, modifier = Modifier.weight(1f), placeholder = { Text("Type a message...") }, enabled = !isLoading, singleLine = false, maxLines = 4)  
                    Spacer(modifier = Modifier.width(8.dp))  
                    IconButton(onClick = {  
                        val text = inputText.trim()  
                        if (text.isEmpty() || isLoading) return@IconButton  
                        val userMessage = ChatMessage(id = UUID.randomUUID().toString(), role = "user", content = text)  
                        messages = messages + userMessage  
                        inputText = ""  
                        isLoading = true  
                        errorMessage = null  
                        scope.launch {  
                            try {  
                                val response = apiService.sendMessage(chatId, text)  
                                val aiMessage = ChatMessage(id = UUID.randomUUID().toString(), role = "assistant", content = response.reply, emotionHint = response.emotion_hint)  
                                messages = messages + aiMessage  
                                localStore.saveChat(chatId, messages)  
                            } catch (e: Exception) {  
                                errorMessage = "Error: ${e.message}"  
                            } finally { isLoading = false }  
                        }  
                    }, enabled = inputText.trim().isNotEmpty() && !isLoading) { Icon(Icons.Default.Send, contentDescription = "Send") }  
                }  
            }  
        }  
    }  
    if (showModelSelector) ModelSelectorDialog(currentModel = currentModel, onModelSelected = { model -> currentModel = model; scope.launch { apiService.setModel(chatId, model) }; showModelSelector = false }, onDismiss = { showModelSelector = false })  
    if (showSettings) SettingsDialog(chatId = chatId, apiService = apiService, onDismiss = { showSettings = false })  
}  
  
@Composable  
fun MessageBubble(message: ChatMessage) {  
    val isUser = message.role == "user"  
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start) {  
        Surface(shape = RoundedCornerShape(16.dp), color = if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant, modifier = Modifier.widthIn(max = 280.dp)) {  
            Column(modifier = Modifier.padding(12.dp)) {  
                Text(text = message.content, color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant)  
                if (!isUser && message.emotionHint != null) { Spacer(modifier = Modifier.height(4.dp)); Text(text = "😊 ${message.emotionHint.primary} (${message.emotionHint.intensity}%)", fontSize = 10.sp, color = if (isUser) MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.7f) else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)) }  
            }  
        }  
    }  
}