function onOpen() {
  try {
    var ui = SpreadsheetApp.getUi();
    if (ui) {
      ui.createMenu("AI Copilot")
        .addItem("Open Copilot", "showCopilotSidebar")
        .addToUi();
    }
  } catch (e) {
    // UI not available in this context (e.g., API execution)
    Logger.log("Cannot create menu: " + e.toString());
  }
}

function showCopilotSidebar() {
  var html =
    HtmlService.createHtmlOutputFromFile("Sidebar").setTitle("Sheet Copilot");
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Gets the current spreadsheet URL and name.
 * Called from the sidebar to display spreadsheet info.
 */
function getSpreadsheetInfo() {
  try {
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    return {
      url: spreadsheet.getUrl(),
      name: spreadsheet.getName(),
    };
  } catch (e) {
    Logger.log("Error getting spreadsheet info: " + e.toString());
    return {
      url: "Unable to get URL",
      name: "Unknown",
    };
  }
}

/**
 * Main handler for chat messages coming from the sidebar.
 * Parses the API response and extracts messages and issues.
 */
function handleUserMessage(userMessage) {
  if (!userMessage) {
    return {
      reply: "Please type something for me to react to.",
      issues: null,
    };
  }

  try {
    // Get spreadsheet context
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var activeSheet = spreadsheet.getActiveSheet();
    var spreadsheetUrl = spreadsheet.getUrl();
    var sheetTitle = activeSheet.getName();

    // Get or create session ID for this spreadsheet
    var sessionId = getOrCreateSessionId(spreadsheet.getId());

    // Make the API call
    var apiResponse = callChatApi(
      userMessage,
      spreadsheetUrl,
      sheetTitle,
      sessionId
    );

    // Parse the API response
    var parsed = parseApiResponse(apiResponse);

    // If issues were detected, highlight them with colors
    if (
      parsed.issues &&
      parsed.issues.potential_errors &&
      parsed.issues.potential_errors.length > 0
    ) {
      try {
        highlightIssues(parsed.issues.potential_errors);
      } catch (colorError) {
        Logger.log("Error highlighting issues: " + colorError.toString());
        // Don't fail the whole request if coloring fails
      }
    }

    return {
      reply: parsed.reply,
      issues: parsed.issues, // { potential_errors: [...] } or null
    };
  } catch (e) {
    Logger.log("Error in handleUserMessage: " + e.toString());
    return {
      reply: "Sorry, I encountered an error: " + e.toString(),
      issues: null,
    };
  }
}

/**
 * Parses the new API response format with messages array.
 * Extracts assistant messages for reply and tool messages for issues.
 */
function parseApiResponse(apiResponse) {
  var reply = "";
  var issues = null;

  if (!apiResponse || !apiResponse.messages) {
    return {
      reply: "No response received from the API.",
      issues: null,
    };
  }

  // Extract assistant messages for the reply
  var assistantMessages = [];
  var toolMessages = [];

  for (var i = 0; i < apiResponse.messages.length; i++) {
    var msg = apiResponse.messages[i];
    if (msg.role === "assistant" && msg.content) {
      assistantMessages.push(msg.content);
    } else if (
      msg.role === "tool" &&
      msg.metadata &&
      msg.metadata.payload &&
      msg.metadata.payload.potential_errors
    ) {
      toolMessages.push(msg.metadata.payload);
    }
  }

  // Combine assistant messages into reply
  if (assistantMessages.length > 0) {
    reply = assistantMessages.join("\n\n");
  } else {
    reply = "Analysis complete.";
  }

  // Extract issues from tool messages
  if (toolMessages.length > 0) {
    // Combine all potential_errors from all tool messages
    var allErrors = [];
    for (var j = 0; j < toolMessages.length; j++) {
      var payload = toolMessages[j];
      if (payload.potential_errors && Array.isArray(payload.potential_errors)) {
        allErrors = allErrors.concat(payload.potential_errors);
      }
    }

    if (allErrors.length > 0) {
      issues = {
        potential_errors: allErrors,
      };
    }
  }

  return {
    reply: reply,
    issues: issues,
  };
}

/**
 * Calls the real chat API endpoint.
 * @param {string} userMessage - The user's message
 * @param {string} spreadsheetUrl - The full URL of the spreadsheet
 * @param {string} sheetTitle - The name of the active sheet
 * @param {string} sessionId - Session ID for maintaining conversation context
 * @return {Object} The API response
 */
function callChatApi(userMessage, spreadsheetUrl, sheetTitle, sessionId) {
  var apiUrl = "https://fintech-hackathon-production.up.railway.app/chat";

  // Build the request payload
  var payload = {
    messages: [
      {
        id: generateMessageId(),
        role: "user",
        content: userMessage,
      },
    ],
    sheetContext: {
      spreadsheetId: spreadsheetUrl,
      sheetTitle: sheetTitle,
    },
    sessionId: sessionId,
  };

  // Set up request options
  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "User-Agent": "insomnia/12.0.0",
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true, // Don't throw on HTTP errors, return response
  };

  // Make the API call
  var response = UrlFetchApp.fetch(apiUrl, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();

  // Check for HTTP errors
  if (responseCode !== 200) {
    Logger.log(
      "API Error - Status: " + responseCode + ", Response: " + responseText
    );
    throw new Error(
      "API request failed with status " + responseCode + ": " + responseText
    );
  }

  // Parse JSON response
  try {
    return JSON.parse(responseText);
  } catch (e) {
    Logger.log("Error parsing API response: " + e.toString());
    throw new Error("Failed to parse API response: " + e.toString());
  }
}

/**
 * Gets or creates a session ID for the current spreadsheet.
 * Uses PropertiesService to persist session ID per spreadsheet.
 * @param {string} spreadsheetId - The spreadsheet ID
 * @return {string} The session ID
 */
function getOrCreateSessionId(spreadsheetId) {
  var properties = PropertiesService.getScriptProperties();
  var key = "sessionId_" + spreadsheetId;
  var sessionId = properties.getProperty(key);

  if (!sessionId) {
    // Generate a new session ID
    sessionId = "session_" + spreadsheetId + "_" + Date.now();
    properties.setProperty(key, sessionId);
  }

  return sessionId;
}

/**
 * Generates a unique message ID.
 * @return {string} A unique message ID
 */
function generateMessageId() {
  return "msg_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
}

/**
 * Highlights issues by calling the color endpoint.
 * @param {Array} issues - Array of issue objects with cell_location and color
 */
function highlightIssues(issues) {
  if (!issues || issues.length === 0) {
    return;
  }

  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var spreadsheetId = spreadsheet.getId();

  // Build color payload from issues - only include issues with URL
  var colorPayload = [];

  for (var i = 0; i < issues.length; i++) {
    var issue = issues[i];
    if (issue.cell_location && issue.color && issue.url) {
      var colorItem = {
        cell_location: issue.cell_location,
        color: issue.color,
        message: issue.title || issue.message || "Issue detected",
        url: issue.url, // Only use issue URL, no fallback
      };
      colorPayload.push(colorItem);
    }
  }

  if (colorPayload.length === 0) {
    Logger.log("No issues with URL found to highlight");
    return;
  }

  // Call color endpoint - send requests grouped by URL
  var urlGroups = {};
  for (var j = 0; j < colorPayload.length; j++) {
    var item = colorPayload[j];
    if (!urlGroups[item.url]) {
      urlGroups[item.url] = [];
    }
    urlGroups[item.url].push(item);
  }

  // Store all responses
  var properties = PropertiesService.getScriptProperties();
  var allResponses = [];

  // Call API for each URL group
  for (var url in urlGroups) {
    var groupPayload = urlGroups[url];
    try {
      var colorResponse = callColorApi(groupPayload);

      if (colorResponse) {
        // Save the entire response
        allResponses.push(colorResponse);

        // Store response data for each cell location in this group
        for (var k = 0; k < groupPayload.length; k++) {
          var cellLoc = groupPayload[k].cell_location;
          var responseKey = "color_response_" + spreadsheetId + "_" + cellLoc;
          properties.setProperty(responseKey, JSON.stringify(colorResponse));

          // Also store snapshot_batch_id for backward compatibility
          if (colorResponse.snapshot_batch_id) {
            var snapshotKey = "snapshot_" + spreadsheetId + "_" + cellLoc;
            properties.setProperty(
              snapshotKey,
              colorResponse.snapshot_batch_id
            );
          }
        }

        Logger.log(
          "Highlighted " +
            groupPayload.length +
            " issue(s) for URL " +
            url +
            " with response: " +
            JSON.stringify(colorResponse)
        );
      }
    } catch (e) {
      Logger.log(
        "Error highlighting issues for URL " + url + ": " + e.toString()
      );
    }
  }
}

/**
 * Calls the color API endpoint to highlight cells.
 * @param {Array} colorPayload - Array of {cell_location, color, message} objects
 * @return {Object} API response with snapshot_batch_id
 */
function callColorApi(colorPayload) {
  var apiUrl =
    "https://fintech-hackathon-production.up.railway.app/tools/color";

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "User-Agent": "insomnia/12.0.0",
    },
    payload: JSON.stringify(colorPayload),
    muteHttpExceptions: true,
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();

  if (responseCode !== 200) {
    Logger.log(
      "Color API Error - Status: " +
        responseCode +
        ", Response: " +
        responseText
    );
    throw new Error("Color API request failed with status " + responseCode);
  }

  try {
    return JSON.parse(responseText);
  } catch (e) {
    Logger.log("Error parsing color API response: " + e.toString());
    throw new Error("Failed to parse color API response");
  }
}

/**
 * Called when user clicks "Fix with AI" or "Ignore" on an issue card.
 * Restores the original cell colors by calling the restore endpoint.
 * @param {string} cellLocation - The cell location (e.g., "A7", "3:6")
 * @param {string} action - The action taken ("fix" or "ignore")
 * @return {Object} Success status
 */
function revertIssueColor(cellLocation, action) {
  Logger.log(
    "Reverting colors for issue at %s with action %s",
    cellLocation,
    action
  );

  try {
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var spreadsheetId = spreadsheet.getId();
    var properties = PropertiesService.getScriptProperties();

    // Get the saved color response for this cell location
    var responseKey = "color_response_" + spreadsheetId + "_" + cellLocation;
    var responseJson = properties.getProperty(responseKey);

    var snapshotBatchId = null;

    if (responseJson) {
      // Parse the saved response
      try {
        var savedResponse = JSON.parse(responseJson);
        snapshotBatchId = savedResponse.snapshot_batch_id;
        Logger.log(
          "Found saved color response for " + cellLocation + ": " + responseJson
        );
      } catch (e) {
        Logger.log("Error parsing saved response: " + e.toString());
      }
    }

    // Fallback to old snapshot_batch_id storage for backward compatibility
    if (!snapshotBatchId) {
      var snapshotKey = "snapshot_" + spreadsheetId + "_" + cellLocation;
      snapshotBatchId = properties.getProperty(snapshotKey);
    }

    if (!snapshotBatchId) {
      Logger.log(
        "No snapshot_batch_id found for cell location: " + cellLocation
      );
      return {
        success: false,
        error: "No snapshot found for this cell location",
        cellLocation: cellLocation,
        action: action,
      };
    }

    // Call restore endpoint
    var restoreResponse = callRestoreApi(snapshotBatchId, [cellLocation]);

    if (restoreResponse && restoreResponse.status === "success") {
      // Remove the stored mappings
      properties.deleteProperty(responseKey);
      var snapshotKey = "snapshot_" + spreadsheetId + "_" + cellLocation;
      properties.deleteProperty(snapshotKey);

      Logger.log("Successfully restored colors for " + cellLocation);
      return {
        success: true,
        cellLocation: cellLocation,
        action: action,
      };
    } else {
      Logger.log("Restore API returned non-success status");
      return {
        success: false,
        error: "Restore API returned non-success status",
        cellLocation: cellLocation,
        action: action,
      };
    }
  } catch (e) {
    Logger.log("Error reverting issue color: " + e.toString());
    return {
      success: false,
      error: e.toString(),
      cellLocation: cellLocation,
      action: action,
    };
  }
}

/**
 * Calls the restore API endpoint to restore cell colors.
 * @param {string} snapshotBatchId - The snapshot batch ID from the color endpoint
 * @param {Array} cellLocations - Array of cell locations to restore (optional, can be null to restore all)
 * @return {Object} API response
 */
function callRestoreApi(snapshotBatchId, cellLocations) {
  var apiUrl =
    "https://fintech-hackathon-production.up.railway.app/tools/restore";

  var payload = {
    snapshot_batch_id: snapshotBatchId,
  };

  // Only include cell_locations if provided
  if (cellLocations && cellLocations.length > 0) {
    payload.cell_locations = cellLocations;
  }

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "User-Agent": "insomnia/12.0.0",
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();

  if (responseCode !== 200) {
    Logger.log(
      "Restore API Error - Status: " +
        responseCode +
        ", Response: " +
        responseText
    );
    throw new Error("Restore API request failed with status " + responseCode);
  }

  try {
    return JSON.parse(responseText);
  } catch (e) {
    Logger.log("Error parsing restore API response: " + e.toString());
    throw new Error("Failed to parse restore API response");
  }
}
