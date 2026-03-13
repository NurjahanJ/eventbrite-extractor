# MCP Server Usage

The Eventbrite Extractor can be run as an **MCP (Model Context Protocol) server**, allowing AI assistants to query Eventbrite data through a standardized interface.

## What is MCP?

MCP is an open protocol that standardizes how AI applications connect to external data sources and tools. It's like a USB-C port for AI — providing a universal way to plug in services.

## Installation

1. **Install the package with MCP support:**

```bash
pip install -e ".[dev]"
```

2. **Set up your API key:**

```bash
cp .env.example .env
# Edit .env and add your Eventbrite API key
```

## Running the MCP Server

### Option 1: Direct Command

```bash
eventbrite-mcp-server
```

The server runs on stdio transport by default, suitable for MCP clients.

### Option 2: Configure in Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "eventbrite-extractor": {
      "command": "eventbrite-mcp-server",
      "env": {
        "EVENTBRITE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Option 3: Use with MCP Inspector

For testing and debugging:

```bash
npx @modelcontextprotocol/inspector eventbrite-mcp-server
```

## Available Tools

### `search_events`

Search for events on Eventbrite.

**Parameters:**
- `keyword` (string, required) — Search query (e.g., "AI", "python", "data science")
- `location` (string, default: "nyc") — "nyc", "worldwide", or a Who's On First place ID
- `max_pages` (int, default: 1) — Number of pages to fetch (1-10)
- `online_only` (bool, default: false) — Only return virtual events
- `free_first` (bool, default: false) — Sort free events first

**Returns:** JSON array of enriched event objects

**Example:**
```json
{
  "tool": "search_events",
  "arguments": {
    "keyword": "machine learning",
    "location": "nyc",
    "max_pages": 2,
    "free_first": true
  }
}
```

### `get_event_by_id`

Fetch a specific event by its Eventbrite ID.

**Parameters:**
- `event_id` (string, required) — The Eventbrite event ID

**Returns:** JSON object with event details

## Available Resources

### `eventbrite://events/ai-nyc`

Get the latest AI events in New York City (up to 20 events).

### `eventbrite://events/{keyword}/{location}`

Get events for a specific keyword and location.

**Examples:**
- `eventbrite://events/python/nyc`
- `eventbrite://events/data-science/worldwide`
- `eventbrite://events/blockchain/85977539` (NYC place ID)

## Available Prompts

### `event_summary_prompt`

Generate a prompt for summarizing events.

**Parameters:**
- `keyword` (string, required) — Event topic
- `location` (string, default: "nyc") — Location filter

### `event_recommendation_prompt`

Generate a prompt for personalized event recommendations.

**Parameters:**
- `interests` (string, required) — User's interests
- `budget` (string, default: "any") — Budget constraint
- `timeframe` (string, default: "next month") — When to attend

## Event Data Schema

Each event returned includes:

```json
{
  "event_id": "1234567890123",
  "title": "AI Workshop",
  "summary": "Learn about AI...",
  "start_date": "2026-03-15",
  "start_time": "14:00",
  "timezone": "America/New_York",
  "venue_name": "Tech Hub NYC",
  "venue_address": "New York, NY, US",
  "is_online": false,
  "organizer_name": "AI Events Co.",
  "url": "https://www.eventbrite.com/e/...",
  "is_free": false,
  "price": "50.00",
  "currency": "USD",
  "category": "Science & Technology",
  "tags": ["AI", "Workshop"],
  "display_price": "$50 USD",
  "display_date": "Sun, Mar 15 at 2:00 PM",
  "display_location": "Tech Hub NYC",
  "event_type": "Workshop"
}
```

## Example AI Assistant Usage

Once configured, you can ask your AI assistant:

> "Find upcoming AI workshops in NYC that are free"

The assistant will use the `search_events` tool:
```json
{
  "keyword": "AI workshop",
  "location": "nyc",
  "free_first": true
}
```

> "What machine learning events are happening worldwide?"

The assistant will call:
```json
{
  "keyword": "machine learning",
  "location": "worldwide",
  "max_pages": 3
}
```

## Troubleshooting

### Server won't start

- Ensure `EVENTBRITE_API_KEY` is set in your environment
- Check that the package is installed: `pip list | grep eventbrite-extractor`
- Verify the MCP SDK is installed: `pip list | grep mcp`

### No events returned

- Verify your API key is valid
- Try a broader search keyword
- Check if you're rate-limited (wait a few minutes)

### Connection issues

- Ensure the server is running with stdio transport
- Check your MCP client configuration
- Review logs for error messages

## Security Notes

- **Never commit** your `.env` file or API keys to version control
- The MCP server inherits environment variables from its parent process
- API keys are passed via environment variables, not command-line arguments
- Rate limits apply — the server caps `max_pages` at 10 to prevent abuse

## Learn More

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Eventbrite API Docs](https://www.eventbrite.com/platform/api)
