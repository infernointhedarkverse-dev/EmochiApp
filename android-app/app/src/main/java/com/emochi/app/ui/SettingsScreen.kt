package com.emochi.app.ui  
  
import androidx.compose.foundation.layout.*  
import androidx.compose.foundation.lazy.LazyColumn  
import androidx.compose.foundation.lazy.items  
import androidx.compose.material3.*  
import androidx.compose.runtime.*  
import androidx.compose.ui.Modifier  
import androidx.compose.ui.text.font.FontWeight  
import androidx.compose.ui.unit.dp  
import com.emochi.app.data.ApiService  
import com.emochi.app.model.BEHAVIOR_TAGS  
import kotlinx.coroutines.launch  
  
@Composable  
fun SettingsDialog(chatId: String, apiService: ApiService, onDismiss: () -> Unit) {  
    val scope = rememberCoroutineScope()  
    var intro by remember { mutableStateOf("") }  
    var personality by remember { mutableStateOf("") }  
    var welcome by remember { mutableStateOf("") }  
    var selectedTags by remember { mutableStateOf<Set<String>>(emptySet()) }  
    var gender by remember { mutableStateOf("neutral") }  
    var isSaving by remember { mutableStateOf(false) }  
      
    AlertDialog(onDismissRequest = onDismiss, title = { Text("Character Settings", fontWeight = FontWeight.Bold) },  
        text = {  
            LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(12.dp)) {  
                item { OutlinedTextField(value = intro, onValueChange = { intro = it }, label = { Text("Character Introduction") }, modifier = Modifier.fillMaxWidth(), placeholder = { Text("e.g., A mysterious traveler...") }, maxLines = 3) }  
                item { OutlinedTextField(value = personality, onValueChange = { personality = it }, label = { Text("Personality Notes") }, modifier = Modifier.fillMaxWidth(), placeholder = { Text("e.g., Confident but insecure...") }, maxLines = 3) }  
                item { OutlinedTextField(value = welcome, onValueChange = { welcome = it }, label = { Text("Welcome Message") }, modifier = Modifier.fillMaxWidth(), placeholder = { Text("e.g., Hello! I'm glad...") }, maxLines = 2) }  
                item { Text("Gender", fontWeight = FontWeight.Medium); Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { listOf("male", "female", "neutral").forEach { g -> FilterChip(selected = gender == g, onClick = { gender = g }, label = { Text(g.replaceFirstChar { it.uppercase() }) }) } } }  
                item { Text("Behavior Tags", fontWeight = FontWeight.Medium); Text("Select tags to modify personality", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)) }  
                items(BEHAVIOR_TAGS.chunked(3)) { tagRow -> Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { tagRow.forEach { tag -> FilterChip(selected = tag in selectedTags, onClick = { selectedTags = if (tag in selectedTags) selectedTags - tag else selectedTags + tag }, label = { Text(tag) }) } } }  
            }  
        },  
        confirmButton = { Button(onClick = { isSaving = true; scope.launch { apiService.setSettings(chatId = chatId, intro = intro.ifBlank { null }, personality = personality.ifBlank { null }, welcome = welcome.ifBlank { null }, tags = selectedTags.toList(), gender = gender); isSaving = false; onDismiss() } }, enabled = !isSaving) { if (isSaving) CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp) else Text("Save") } },  
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } })  
}