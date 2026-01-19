# Waste Classification System for Hong Kong

An enterprise-grade multimodal AI application that classifies waste items according to Hong Kong's official waste management regulations. Built with LLM technology and Retrieval-Augmented Generation (RAG), the system provides accurate bin recommendations based on official Environmental Protection Department (EPD) guidelines.

## Features

- **Dual Input Modes**: Text descriptions or image uploads
- **Multi-Item Detection**: Automatic identification and classification of multiple items
- **Context-Aware**: Intelligent detection of associated items (packaging, instructions, containers)
- **RAG-Enhanced**: Vector similarity search improves classification accuracy
- **EPD Compliant**: Fully aligned with Hong Kong official waste management guidelines

## Tech Stack

- **Frontend**: Next.js 14+, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.11+)
- **Vector DB**: ChromaDB
- **LLM**: OpenRouter API (supports any compatible model, local GPU models via Ollama/vLLM)
- **Embeddings**: sentence-transformers (local, GPU-accelerated)
- **Infrastructure**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- OpenRouter API key ([Get one here](https://openrouter.ai))
- 4GB+ disk space, 2GB+ RAM

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/nolanimage/hk-waste-classification-system.git
   cd hk-waste-classification-system
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Deploy**
   ```bash
   docker-compose up --build -d
   ```

4. **Access**
   - Web Interface: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## Usage

### Web Interface

Navigate to http://localhost:3000, select text or image input, submit, and review color-coded bin recommendations with detailed explanations.

### API

**POST** `/api/classify`

```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "aluminum can and plastic bottle"}'
```

**Response:**
```json
{
  "items": [
    {
      "item": "Aluminum can",
      "category": "metal",
      "bin": "Yellow bin (aluminum/metal cans)",
      "binColor": "yellow",
      "explanation": "Aluminum cans should be placed in the yellow bin for metal recycling. Must be empty and clean.",
      "confidence": null
    },
    {
      "item": "Plastic water bottle",
      "category": "plastic",
      "bin": "Brown bin (plastic bottles)",
      "binColor": "brown",
      "explanation": "Plastic bottles should be placed in the brown bin for plastic recycling. Must be empty and clean.",
      "confidence": null
    }
  ],
  "total_items": 2,
  "input_type": "text"
}
```

## Hong Kong Waste Management

This system implements official [EPD guidelines](https://www.wastereduction.gov.hk/en-hk/recycling-tips).

### Three-Colour Bins

- **Blue Bin**: Clean, dry waste paper (newspapers, magazines, cardboard). NOT: wet paper, plastic-lined paper, composite materials
- **Yellow Bin**: Empty, clean aluminum and metal cans. NOT: other metal items (use GREEN@COMMUNITY)
- **Brown Bin**: Empty, clean plastic bottles (PET #1, HDPE #2). NOT: other plastics (use GREEN@COMMUNITY or general waste)

### GREEN@COMMUNITY

Separate collection points for: glass bottles, electronics, batteries, beverage cartons (Tetra Pak), fluorescent lamps, and other recyclables not accepted in three-colour bins.

### Rules

1. Items must be clean and dry for three-colour bins
2. Contaminated items go to general waste
3. Composite materials should be separated when possible
4. Place items directly in bins (not in plastic bags)
5. When uncertain, recommend GREEN@COMMUNITY consultation

**References:**
- [EPD Recycling Tips](https://www.wastereduction.gov.hk/en-hk/recycling-tips)
- [Clean Recycling Tips PDF](https://www.wastereduction.gov.hk/sites/default/files/one-stop-shop/1_Pager_on_Clean_Recycling_Tips.pdf)

## Configuration

### Environment Variables

- **`OPENROUTER_API_KEY`** (Required) - OpenRouter API authentication key
- **`VISION_MODEL`** (Optional, default: `qwen/qwen3-vl-32b-instruct`) - Vision model for images
- **`TEXT_MODEL`** (Optional, default: `qwen/qwen-2.5-7b-instruct`) - Text classification model
- **`ITEM_DETECTION_MODEL`** (Optional, default: `qwen/qwen-2.5-72b-instruct`) - Multi-item detection
- **`EMBEDDING_MODEL`** (Optional, default: `all-MiniLM-L6-v2`) - Local embedding model
- **`CHROMA_DB_PATH`** (Optional, default: `./chroma_db`) - Vector database path
- **`PORT`** (Optional, default: `8000`) - Backend server port

### Model Selection

- **OpenRouter Models**: Any compatible model can be configured via environment variables
- **Local GPU Models**: Architecture supports local models (Ollama, vLLM, TensorRT-LLM) with GPU acceleration
- **Requirements**: Vision models need multimodal capabilities; detection models benefit from larger sizes (70B+)

## Operations

```bash
# Service management
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f       # View logs
docker-compose restart [svc]  # Restart service

# Database
docker-compose exec backend python -m app.services.seed_data  # Re-seed
rm -rf backend/chroma_db && docker-compose up -d             # Reset

# Health check
curl http://localhost:8000/health
```

## Troubleshooting

- **UI not updating**: Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
- **API errors**: Verify `OPENROUTER_API_KEY` in `.env` and check credits
- **Classification failures**: Check logs with `docker-compose logs backend`
- **Database issues**: Reset database (see Operations section)
- **Slow responses**: Optimize images, consider model selection
- **High API costs**: Implement caching, optimize model selection

## Architecture

**Text Flow**: User input → Item detection → Embedding generation → RAG retrieval → LLM classification → Aggregated results

**Image Flow**: Image upload → Object detection → Image cropping → Embedding generation → RAG retrieval → Vision model classification → Results with bounding boxes

**RAG System**: ChromaDB stores examples, sentence-transformers generates embeddings, top-K similarity search retrieves relevant examples for LLM prompts.

## Project Structure

```
hk-waste-classification-system/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── docker-compose.yml
└── README.md
```

## Contributing

We welcome contributions! Fork the repository, create a feature branch, make your changes, and submit a pull request.

**Areas for contribution**: Classification accuracy, feature development, documentation, bug fixes, performance optimization, UI/UX improvements, testing.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hong Kong Environmental Protection Department for official guidelines
