# Zelda Tears of the Kingdom: ETL-project
An end-to-end ETL pipeline analyzing armor value and progression efficiency in The Legend of Zelda: Tears of the Kingdom to determine which items players should prioritize for optimal gameplay.
# ![Image](https://github.com/user-attachments/assets/c73e8220-0be4-4ad9-9626-822ffbc0577d) The Legend of Zelda: Tears of the Kingdom ETL Pipeline

# Optimizing Armor Investment in The Legend of Zelda: Tears of the Kingdom
## 🗡️ Project Overview

**Hypothesis:**
What clothing/armor items in The Legend of Zelda: Tears of the Kingdom are most valuable for progressing through the main quests? Which items should players prioritize acquiring to save time, energy, and in-game resources?

While The Legend of Zelda is designed for exploration — cooking, resting, discovering armor organically — this project approaches the game from a data perspective.

As a player, I found myself purchasing armor that didn’t meaningfully advance gameplay. Sometimes it was for customization (which is fun), but this time I wanted to optimize for quest progression rather than cosmetics.

**The objective is to determine:**
- What armor is essential?
- What armor is optional but helpful?
- What armor is primarily cosmetic?
- What is the most efficient acquisition strategy?

## ![Image](https://github.com/user-attachments/assets/2efe80f5-8047-4f21-a642-08717c9709ce) The Problem

In _Tears of the Kindgom_, environmental conditions and quest mechanics often require specific armor sets.

**Examples:**

- Hebra Mountains → Cold resistance required (Snowquill Set)
- Death Mountain (Eldin Region) → Flame resistance required (Flamebreaker Set)
- Gerudo Desert → Heat resistance (day) + Cold resistance (night) (Desert Voe Set, Warm Doublet)
- Zora’s Domain → Zora Armor required to swim up waterfalls (main quest progression)
- Yiga Clan Hideout → Stealth Set highly beneficial
- Heavy climbing regions → Climber’s Set reduces stamina drain

Each major region introduces survival-based armor. However, not every set is required to complete the main storyline.

Without clear prioritization, players can spend rupees on armor that looks good but does not significantly improve game progression.

## Project Goal

**This ETL project will:**

1. Extract armor data
2. Transform it into structured datasets
3. Load it into a database for analysis
4. Rank armor based on:

- Main quest dependency
- Environmental necessity
- Combat utility
- Cost efficiency

**Tech Stack:**
- Python
- Pandas (data transformation)
- SQLite (data storage)
- Flask (API layer)
- Jupyter Notebook (EDA and analysis)
- SQL (querying and scoring)
  
## Key insights

Most cost-efficient armor piece: Hylian Hood (highest defense per rupee)

Best early-game armor investment: Hylian Set pieces

Best combat protection: Soldier’s Set (highest defense but more expensive

## Future Expansion Ideas
- **Armor upgrade analysis:** Evaluate which armor pieces can be upgraded and how upgrades impact total defense and value. Incorporate upgrade material requirements to estimate the true cost of progression and identify which items players should prioritize collecting to maximize defense gains and long-term return on investment.
- **Progression-aware recommendations:** Recommend armor to the player that maximizes defense ROI under common rupee constraints.
- **Armor clustering (K-means):** Cluster armor into archetypes (e.g., budget-efficient basics, high-upgrade late-game gear, shop items) using standardized numeric features and categories.
- **LLM explanation layer:** Add an optional AI “interpreter” that summarizes API results in plain English and explains *why* an item ranks highly using computed metrics (defense/rupee, upgrade potential).
