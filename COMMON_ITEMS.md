# Common Items Detected by the System

This document lists common waste items that the system can classify, based on the seed data and items detected during operation.

## Items by Category

### Metal Items (Yellow Bin)
- **Aluminum soda can** - Must be empty and clean
- **Metal can (food)** - Empty metal food can, rinse if necessary
- **Metal wire hanger** - Metal clothes hanger
- **Aluminum foil** - Must be clean (if contaminated, goes to general waste)

### Plastic Items (Brown Bin - Plastic Bottles Only)
- **Plastic water bottle** - Clear plastic water bottle
- **Plastic bottle with cap** - Remove cap if different material
- **Plastic container** - Note: Only bottles go in brown bin, other containers may need GREEN@COMMUNITY

### Paper Items (Blue Bin)
- **Newspaper** - Must be dry and clean
- **Cardboard box** - Flatten before recycling, remove tape/plastic labels
- **Magazine** - Must be dry, remove plastic covers
- **Office paper** - White office paper, remove staples if possible
- **Contaminated paper** - Paper with food stains goes to general waste (NOT recyclable)

### Glass Items (GREEN@COMMUNITY)
- **Glass bottle** - Wine bottle or other glass containers
- **Broken glass** - Wrap in newspaper for safety

### Electronics & Batteries (GREEN@COMMUNITY)
- **Battery** - Used AA/AAA batteries
- **Electronic device** - Mobile phone or small electronic device

### Cartons (GREEN@COMMUNITY)
- **Tetra Pak carton** - Milk or juice carton, rinse and flatten

### General Waste (Not Recyclable)
- **Styrofoam container** - Takeout containers
- **Plastic bag** - Single-use plastic bags
- **Coffee cup (disposable)** - Cups with plastic lining
- **Food scraps** - Leftover food waste (use food waste bin if available)

## Items by Bin Color

### Blue Bin (Waste Paper)
- Newspaper
- Cardboard box
- Magazine
- Office paper

### Yellow Bin (Aluminum/Metal Cans)
- Aluminum soda can
- Metal can (food)
- Metal wire hanger
- Aluminum foil

### Brown Bin (Plastic Bottles)
- Plastic water bottle
- Plastic bottle with cap
- Plastic container (note: only bottles accepted)

### GREEN@COMMUNITY
- Glass bottle
- Broken glass
- Battery
- Electronic device
- Tetra Pak carton

### General Waste (Other)
- Styrofoam container
- Plastic bag
- Coffee cup (disposable)
- Food scraps
- Contaminated paper

## Total Items in System

**Seed Data**: 21 items
**Auto-enriched**: Items added automatically when high-confidence classifications are detected

## How to View Current Items

### Via API
```bash
# Get all examples
curl http://localhost:8000/api/admin/examples

# Get statistics
curl http://localhost:8000/api/admin/statistics
```

### Statistics Endpoint Returns
- Total number of examples
- Unique items count
- Items grouped by category
- Items grouped by bin color
- Items grouped by bin type
- Complete list of all items

## Notes

- The system automatically enriches the database with high-confidence classifications
- Items are checked for duplicates before being added
- The database grows over time as more items are classified
- Check the statistics endpoint to see the current state of the database
