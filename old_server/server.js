// import express from "express";
// import cors from "cors";
// import multer from "multer";
// import dotenv from "dotenv";
// import { v4 as uuidv4 } from "uuid";
// import chat from "./chat.js";

// dotenv.config();

// const app = express();
// app.use(cors());
// app.use(express.json());

// // config multer to store on local disk
// const storage = multer.diskStorage({
//   destination: (req, file, cb) => {
//     cb(null, "uploads/");
//   },
//   filename: (req, file, cb) => {
//     // generate unique filename to avoid collisions
//     const uniqueName = `${uuidv4()}-${file.originalname}`;
//     cb(null, uniqueName);
//   },
// });

// const upload = multer({ storage });

// const PORT = 5001;

// // Map to store fileId -> {path, filename, uploadedAt}
// const fileRegistry = {};

// /**
//  * Option 1: POST /chat - atomic: upload file + ask question together
//  * Client sends: multipart/form-data { file, question }
//  * Returns: { fileId, ragAnswer, mcpAnswer }
//  */
// app.post("/chat", upload.single("file"), async (req, res) => {
//   try {
//     // Validate inputs
//     if (!req.file) {
//       return res.status(400).send({ error: "No file uploaded" });
//     }
//     if (!req.body.question) {
//       return res.status(400).send({ error: "No question provided" });
//     }

//     const fileId = uuidv4();
//     const filePath = req.file.path;

//     // Register the file
//     fileRegistry[fileId] = {
//       path: filePath,
//       filename: req.file.originalname,
//       uploadedAt: new Date().toISOString(),
//     };

//     // Process the query against the uploaded file
//     const resp = await chat(filePath, req.body.question);

//     res.send({
//       fileId,
//       filename: req.file.originalname,
//       ragAnswer: resp.text,
//       mcpAnswer: "N/A",
//     });
//   } catch (error) {
//     console.error("Error in /chat POST:", error);
//     res.status(500).send({ error: "Failed to process chat request" });
//   }
// });

// /**
//  * Option 2: GET /chat - select existing file to ask a question
//  * Client sends: GET /chat?fileId=<id>&question=<query>
//  * Returns: { ragAnswer, mcpAnswer }
//  */
// app.get("/chat", async (req, res) => {
//   try {
//     const { fileId, question } = req.query;

//     // Validate inputs
//     if (!fileId) {
//       return res.status(400).send({ error: "fileId query parameter required" });
//     }
//     if (!question) {
//       return res
//         .status(400)
//         .send({ error: "question query parameter required" });
//     }

//     // Check if file exists in registry
//     if (!fileRegistry[fileId]) {
//       return res.status(404).send({ error: "File not found" });
//     }

//     const filePath = fileRegistry[fileId].path;

//     // Process the query against the existing file
//     const resp = await chat(filePath, question);

//     res.send({
//       fileId,
//       filename: fileRegistry[fileId].filename,
//       ragAnswer: resp.text,
//       mcpAnswer: "N/A",
//     });
//   } catch (error) {
//     console.error("Error in /chat GET:", error);
//     res.status(500).send({ error: "Failed to process chat request" });
//   }
// });

// /**
//  * GET /files - list all uploaded files
//  * Returns: array of {fileId, filename, uploadedAt}
//  */
// app.get("/files", (req, res) => {
//   const filesList = Object.entries(fileRegistry).map(([fileId, data]) => ({
//     fileId,
//     filename: data.filename,
//     uploadedAt: data.uploadedAt,
//   }));
//   res.send(filesList);
// });

// /**
//  * DELETE /files/:fileId - delete a file from registry (optional)
//  */
// // app.delete("/files/:fileId", (req, res) => {
// //   const { fileId } = req.params;
// //   if (!fileRegistry[fileId]) {
// //     return res.status(404).send({ error: "File not found" });
// //   }
// //   delete fileRegistry[fileId];
// //   res.send({ message: "File deleted successfully" });
// // });

// app.listen(PORT, () => {
//   console.log(`Server running on port ${PORT}`);
// });

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import multer from "multer";
import chat from "./chat.js";
import chatMCP from "./chat-mcp.js";

dotenv.config();

const app = express();
app.use(cors());

// Configure multer
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "uploads/");
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  },
});
const upload = multer({ storage: storage });

const PORT = 5001;

let filePath = "./uploads/Simon1983.pdf";

app.post("/upload", upload.single("file"), (req, res) => {
  // Use multer to handle file upload
  filePath = req.file.path; // The path where the file is temporarily saved
  res.send(filePath + " upload successfully.");
});

app.get("/chat", async (req, res) => {
  const resp = await chat(filePath, req.query.question); // Use RAG chat
  const respmcp = await chatMCP(req.query.question); // Use MCP-enhanced chat

  res.send({
    ragAnswer: resp.text,
    mcpAnswer: respmcp.text,
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
