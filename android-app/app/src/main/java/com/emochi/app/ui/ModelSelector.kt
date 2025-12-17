package com.emochi.app.ui  
  
import androidx.compose.foundation.clickable  
import androidx.compose.foundation.layout.*  
import androidx.compose.foundation.lazy.grid.GridCells  
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid  
import androidx.compose.foundation.lazy.grid.items  
import androidx.compose.material3.*  
import androidx.compose.runtime.Composable  
import androidx.compose.ui.Modifier  
import androidx.compose.ui.text.font.FontWeight  
import androidx.compose.ui.unit.dp  
import androidx.compose.ui.unit.sp  
import com.emochi.app.model.PERSONALITY_MODELS  
  
@Composable  
fun ModelSelectorDialog(currentModel: String, onModelSelected: (String) -> Unit, onDismiss: () -> Unit) {  
    AlertDialog(onDismissRequest = onDismiss, title = { Text("Select Personality Model", fontWeight = FontWeight.Bold) },  
        text = { LazyVerticalGrid(columns = GridCells.Fixed(2), contentPadding = PaddingValues(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {  
            items(PERSONALITY_MODELS) { model -> ModelCard(model = model, isSelected = model == currentModel, onClick = { onModelSelected(model) }) }  
        } }, confirmButton = { TextButton(onClick = onDismiss) { Text("Close") } })  
}  
  
@Composable  
fun ModelCard(model: String, isSelected: Boolean, onClick: () -> Unit) {  
    val emoji = when (model) {  
        "Vanilla" -> "🍦"; "Vanilla Short" -> "⚡"; "Matcha" -> "🍵"; "Strawberry" -> "🍓"; "Chocolate" -> "🍫"; "Peach" -> "🍑"; "Mint" -> "🌿"; "Blueberry" -> "🫐"; "Blackberry" -> "🖤"; "Rainbow" -> "🌈"; "Unicorn" -> "🦄"; "Sage" -> "🧙"; else -> "🎭"  
    }  
    Card(modifier = Modifier.fillMaxWidth().clickable(onClick = onClick), colors = if (isSelected) CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer) else CardDefaults.cardColors()) {  
        Column(modifier = Modifier.padding(12.dp)) { Text(text = emoji, fontSize = 32.sp); Spacer(modifier = Modifier.height(4.dp)); Text(text = model, fontSize = 14.sp, fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal) }  
    }  
}