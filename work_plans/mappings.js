function mapFunctions(inputText) {
  var functionsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("functions");
  var functionNames = inputText.split(',');
  var mappings = [];

  for (var i = 0; i < functionNames.length; i++) {
    var functionName = functionNames[i].trim();
    var rowNumber = -1; // Initialize with -1 to detect if the function name is not found
    
    // Search for the row number of the function name in functions!B:B
    var functionNamesColumn = functionsSheet.getRange("B:B").getValues();
    for (var j = 0; j < functionNamesColumn.length; j++) {
      if (functionNamesColumn[j][0] === functionName) {
        rowNumber = j + 1; // Add 1 to convert from zero-based index to row number
        break;
      }
    }
    
    if (rowNumber !== -1) {
      // Get the corresponding mapping from functions!A:A
      var mapping = functionsSheet.getRange("A" + rowNumber).getValue();
      mappings.push(mapping);
    } else {
      mappings.push("no mapping found");
    }
  }
  
  // Join the mappings into a comma-separated string
  var result = mappings.join(',');
  
  // Log the result for debugging
  Logger.log("Input Text: " + inputText + " | Mappings: " + result);
  
  return result;
}


