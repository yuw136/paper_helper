import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { getJson } from "serpapi";

const SERPAPI_KEY = process.env.SERPAPI_KEY;
const server = new McpServer({
  name: "serpapi-server",
  version: "1.0.0",
});
server.registerTool(
  "search_web",
  {
    description:
      "Search the web using SerpAPI. Returns search results including organic results, snippets, and related information.",
    inputSchema: {
      query: z.string().describe("The search query to execute"),
      num: z
        .number()
        .optional()
        .describe("Number of results to return (default: 10)"),
    },
  },
  async ({ query, num }) => {
    try {
      const results = await getJson({
        engine: "google",
        q: query,
        num,
        api_key: SERPAPI_KEY,
      });

      const fullResults = JSON.stringify(results);

      return {
        content: [{ type: "text", text: fullResults }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: "something went wrong" }],
      };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SerpAPI running on stdio");
}

main().catch((error) => {
  console.error("MCP Server error:", error);
  process.exit(1);
});

export default server;
