# Waste Classification System for Hong Kong

An enterprise-grade multimodal AI application that classifies waste items according to Hong Kong's official waste management regulations. Built with state-of-the-art LLM technology and Retrieval-Augmented Generation (RAG), the system provides accurate, compliant bin recommendations based on official Environmental Protection Department (EPD) guidelines.

## Overview

This production-ready system enables users to classify single or multiple waste items through text descriptions or image uploads. The application automatically detects associated items (e.g., packaging, instructions, containers) and provides detailed classification results with bin recommendations, explanations, and confidence scores.

## Key Features

- **Dual Input Modes**: Text descriptions or image uploads (mutually exclusive)
- **Multi-Item Detection**: Automatic identification and classification of multiple items from a single input
- **Context-Aware Classification**: Intelligent detection of associated items and components
- **RAG-Enhanced Accuracy**: Vector similarity search retrieves relevant examples to improve classification precision
- **Regulatory Compliance**: Fully aligned with Hong Kong EPD official waste management guidelines
- **Production Architecture**: Containerized microservices with health checks and error handling

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS
- **Runtime**: React 18+

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Vector Database**: ChromaDB for RAG storage and retrieval
- **LLM Integration**: OpenRouter API with flexible model selection
  - Vision: `qwen/qwen3-vl-32b-instruct` (image classification)
  - Text: `qwen/qwen-2.5-7b-instruct` (text classification)
  - Detection: `qwen/qwen-2.5-72b-instruct` (multi-item detection)
  - **Model Flexibility**: Any OpenRouter-compatible model can be configured
  - **Local GPU Support**: Can be adapted to use local models with GPU acceleration (Ollama, vLLM, etc.)
- **Embeddings**: sentence-transformers (local execution, GPU-accelerated when available)
- **Image Processing**: Pillow, OpenCV

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Multi-container architecture with health checks

## System Requirements

### Minimum Requirements (API-based)
- Docker Engine 20.10+ and Docker Compose 2.0+
- OpenRouter API account with active API key
- Minimum 4GB available disk space
- 2GB+ RAM recommended

### Recommended for Local Models (GPU)
- NVIDIA GPU with CUDA support (8GB+ VRAM recommended)
- CUDA Toolkit 11.8+ or 12.0+
- 16GB+ system RAM
- 20GB+ available disk space (for model storage)
- Docker with GPU support (nvidia-docker2)

## Installation

### Prerequisites

1. Install Docker and Docker Compose:
   ```bash
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. Obtain OpenRouter API key:
   - Register at [OpenRouter.ai](https://openrouter.ai)
   - Generate API key from dashboard
   - Ensure sufficient credits for API usage

### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/nolanimage/hk-waste-classification-system.git
   cd hk-waste-classification-system
   ```

2. **Configure Environment**
   
   Create `.env` file in project root:
   ```bash
   # Copy the example file and edit it
   cp .env.example .env
   # Then edit .env and add your OpenRouter API key
   ```
   
   Or create `.env` manually with the following structure:
   ```bash
   # Required: OpenRouter API Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key_here

   # Optional: Model Configuration (defaults provided)
   # Models can be changed to any OpenRouter-compatible model
   # For local GPU models, modify API client to use local endpoints (Ollama, vLLM, etc.)
   VISION_MODEL=qwen/qwen3-vl-32b-instruct
   TEXT_MODEL=qwen/qwen-2.5-7b-instruct
   ITEM_DETECTION_MODEL=qwen/qwen-2.5-72b-instruct
   EMBEDDING_MODEL=all-MiniLM-L6-v2

   # Optional: Database and Server Configuration
   CHROMA_DB_PATH=./chroma_db
   PORT=8000
   ```

3. **Deploy Application**
   ```bash
   docker-compose up --build -d
   ```

   This command will:
   - Build optimized production images for frontend and backend
   - Initialize ChromaDB vector database
   - Seed database with classification examples
   - Start services with health monitoring

4. **Verify Deployment**
   ```bash
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

5. **Access Application**
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Health Endpoint: http://localhost:8000/health

## Usage

### Web Interface

1. Navigate to http://localhost:3000
2. Select input method:
   - **Text**: Enter item descriptions (e.g., "aluminum can, plastic bottle, newspaper")
   - **Image**: Upload JPEG/PNG image containing waste items
3. Submit classification request
4. Review results:
   - Itemized classifications with bin recommendations
   - Color-coded bin assignments
   - Detailed explanations per item
   - Confidence scores (when available)

### API Integration

#### Classification Endpoint

**POST** `/api/classify`

**Request Body:**
```json
{
  "text": "string (optional)",
  "image": "string (base64 encoded, optional)"
}
```

**Constraints:**
- Exactly one of `text` or `image` must be provided
- Image must be base64 encoded with data URI prefix
- Maximum text length: 1000 characters (recommended)

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "aluminum soda can and plastic water bottle"
  }'
```

**Response Schema:**
```json
{
  "items": [
    {
      "item": "Aluminum soda can",
      "category": "metal",
      "bin": "Yellow bin (aluminum/metal cans)",
      "binColor": "yellow",
      "explanation": "Aluminum cans should be placed in the yellow bin for metal recycling. Must be empty and clean.",
      "confidence": 0.95,
      "bbox": null
    }
  ],
  "total_items": 2,
  "input_type": "text"
}
```

#### Admin Endpoints

**POST** `/api/admin/add-example` - Add classification example to RAG database

**GET** `/api/admin/examples` - Retrieve all examples in database

**GET** `/health` - Service health check

## Hong Kong Waste Management Classification

This system implements the official classification rules from the [Hong Kong Environmental Protection Department](https://www.wastereduction.gov.hk/en-hk/recycling-tips).

### Three-Colour Bin System

#### Blue Bin - Waste Paper
**Accepted Items:**
- Newspapers, magazines, office paper
- Cardboard boxes, paper bags, envelopes
- Books (hard covers removed)

**Excluded Items:**
- Wet or soiled paper
- Plastic-lined paper (e.g., coated coffee cups)
- Composite materials
- Food containers with residue
- Thermal paper, laminated paper

**Requirements:** Clean, dry, contamination-free

#### Yellow Bin - Metal Cans
**Accepted Items:**
- Aluminum beverage cans
- Metal food cans
- Must be empty, clean, and rinsed

**Excluded Items:**
- Scrap metal, large metal objects
- Metal utensils, wires, or non-can containers
- These items require GREEN@COMMUNITY facilities

**Requirements:** Empty, clean, rinsed, preferably flattened

#### Brown Bin - Plastic Bottles
**Accepted Items:**
- Plastic bottles (PET #1, HDPE #2)
- Must display recycling symbols
- Must be empty and clean

**Excluded Items:**
- Plastic containers, bags, toys
- Styrofoam, plastic utensils, packaging film
- These typically go to GREEN@COMMUNITY or general waste

**Requirements:** Empty, clean, rinsed, caps removed if different material

### GREEN@COMMUNITY Facilities

Separate collection points (not three-colour bins) for:
- Glass bottles and containers (clean, rinsed)
- Small electrical appliances and electronics
- All battery types (rechargeable, single-use, automotive)
- Beverage cartons (Tetra Pak, aseptic packaging)
- Fluorescent lamps and tubes
- Other recyclables not accepted in three-colour bins

### Classification Rules

1. **Cleanliness Requirement**: All items for three-colour bins must be clean and dry
2. **Contamination Protocol**: Contaminated items route to general waste
3. **Separation Guidelines**: Composite materials should be separated when possible
4. **Bagging Restriction**: Items must be placed directly in bins, not in plastic bags
5. **Uncertainty Handling**: When classification is uncertain, recommend GREEN@COMMUNITY consultation

**Official Documentation:**
- [EPD Recycling Tips](https://www.wastereduction.gov.hk/en-hk/recycling-tips)
- [Clean Recycling Tips PDF](https://www.wastereduction.gov.hk/sites/default/files/one-stop-shop/1_Pager_on_Clean_Recycling_Tips.pdf)

## Architecture

### System Flow

**Text Input Processing:**
1. User submits text description
2. Item detection service identifies all items and associated components
3. For each item:
   - Generate text embedding via sentence-transformers
   - Retrieve similar examples from ChromaDB using vector similarity
   - Classify using LLM with retrieved context
4. Aggregate results into structured response

**Image Input Processing:**
1. User uploads image
2. Vision model detects objects and generates bounding boxes
3. Each detected object is cropped from original image
4. For each object:
   - Generate description embedding
   - Retrieve similar examples from RAG database
   - Classify using vision model with cropped image and context
5. Return classifications with spatial information

### RAG System

- **Storage**: ChromaDB vector database
- **Embeddings**: sentence-transformers (local execution)
- **Retrieval**: Top-K similarity search (default: 5 examples)
- **Enhancement**: Retrieved examples included in LLM prompts for improved accuracy

## Project Structure

```
hk-waste-classification-system/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   └── lib/              # API client
│   └── Dockerfile
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── routers/         # API endpoints
│   │   └── services/        # Business logic
│   ├── data/                # Seed data
│   └── Dockerfile
├── docker-compose.yml       # Orchestration
└── README.md
```

## Configuration

### Environment Variables

- **`OPENROUTER_API_KEY`** (Required)
  - Description: OpenRouter API authentication key
  - Default: None (must be provided)

- **`VISION_MODEL`** (Optional)
  - Description: Vision model identifier for image classification
  - Default: `qwen/qwen3-vl-32b-instruct`

- **`TEXT_MODEL`** (Optional)
  - Description: Text classification model for text-only inputs
  - Default: `qwen/qwen-2.5-7b-instruct`

- **`ITEM_DETECTION_MODEL`** (Optional)
  - Description: Model for multi-item detection and associated item identification
  - Default: `qwen/qwen-2.5-72b-instruct`

- **`EMBEDDING_MODEL`** (Optional)
  - Description: Sentence-transformers model for local text embeddings
  - Default: `all-MiniLM-L6-v2`
  - Options: `all-MiniLM-L6-v2` (fast), `all-mpnet-base-v2` (more accurate)

- **`CHROMA_DB_PATH`** (Optional)
  - Description: Path to ChromaDB vector database storage
  - Default: `./chroma_db`

- **`PORT`** (Optional)
  - Description: Backend server port number
  - Default: `8000`

### Model Selection

Models can be customized via environment variables. The system supports:

**OpenRouter API Models:**
- Any model available on the OpenRouter platform
- Simply update the model identifier in environment variables
- Examples: `gpt-4-vision-preview`, `claude-3-opus`, `llama-3-70b-instruct`
- Ensure selected models are compatible with your use case and within API credit budget

**Local Model Support:**
- The architecture can be adapted to use local models with GPU acceleration
- Compatible with local inference servers (Ollama, vLLM, TensorRT-LLM)
- For local deployment, modify the API client to point to your local endpoint
- GPU acceleration recommended for local models (CUDA-compatible GPUs)
- Local models eliminate API costs but require sufficient GPU memory

**Model Configuration Tips:**
- Vision models: Require multimodal capabilities (image + text)
- Text models: Standard language models work well for text classification
- Detection models: Larger models (70B+) provide better multi-item detection
- Embedding models: `all-MiniLM-L6-v2` (fast) or `all-mpnet-base-v2` (accurate)

## Operations

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild after code changes
docker-compose up -d --build
```

### Database Management

```bash
# Re-seed database
docker-compose exec backend python -m app.services.seed_data

# Reset database (deletes all data)
docker-compose down
rm -rf backend/chroma_db
docker-compose up -d
```

### Health Monitoring

```bash
# Check service health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

## Troubleshooting

### Frontend Issues

**Problem**: UI not updating after changes
- **Solution**: Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
- **Alternative**: Clear browser cache or use incognito mode

**Problem**: Build failures
- **Solution**: Rebuild with no cache: `docker-compose build --no-cache frontend`

### Backend Issues

**Problem**: API authentication errors
- **Solution**: Verify `OPENROUTER_API_KEY` in `.env` file
- **Check**: Ensure API key has sufficient credits

**Problem**: Classification failures
- **Solution**: Check backend logs: `docker-compose logs backend`
- **Verify**: Model availability on OpenRouter platform

**Problem**: Database errors
- **Solution**: Reset database (see Database Management section)
- **Check**: Verify disk space availability

### Performance Issues

**Problem**: Slow classification responses
- **Cause**: Large images or multiple items
- **Solution**: Optimize images before upload, consider model selection

**Problem**: High API costs
- **Solution**: Implement caching layer, optimize model selection
- **Monitor**: Track API usage via OpenRouter dashboard

## Security Considerations

- **API Keys**: Never commit `.env` files to version control
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Consider implementing rate limits for production
- **CORS**: Configured for localhost development; update for production

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or enhancing the classification accuracy, your contributions are valuable.

### How to Contribute

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Branch**: Work on a feature branch (`git checkout -b feature/your-feature-name`)
3. **Make Changes**: Implement your improvements with clear, documented code
4. **Test Thoroughly**: Ensure all functionality works as expected
5. **Submit a Pull Request**: Provide a clear description of your changes

### Areas for Contribution

- **Classification Accuracy**: Add new seed examples or improve existing ones
- **Feature Development**: Implement new features from the roadmap
- **Documentation**: Improve README, add code comments, or create tutorials
- **Bug Fixes**: Identify and fix issues
- **Performance**: Optimize code, add caching, or improve response times
- **UI/UX**: Enhance the user interface and user experience
- **Testing**: Add unit tests, integration tests, or E2E tests

### Code Standards

- Follow existing code style and conventions
- Write clear, self-documenting code with comments where needed
- Ensure backward compatibility when possible
- Update documentation for any API or behavior changes

### Questions or Suggestions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about implementation
- Documentation improvements

We appreciate your interest in making this project better for the Hong Kong community!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hong Kong Environmental Protection Department for official waste management guidelines
- OpenRouter for LLM API infrastructure
- ChromaDB for vector database technology
- sentence-transformers for local embedding capabilities

## References

- [Hong Kong EPD Recycling Guidelines](https://www.wastereduction.gov.hk/en-hk/recycling-tips)
- [EPD Clean Recycling Tips PDF](https://www.wastereduction.gov.hk/sites/default/files/one-stop-shop/1_Pager_on_Clean_Recycling_Tips.pdf)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
