// Generated from your uploaded CSV: "Untitled spreadsheet - Sheet1.csv" (50 states)
const STATE_THEMES = {
    "Alabama": {
      "inspiration": "Coast + History",
      "colors": {
        "primary": "#0A4C6A",
        "secondary": "#1F8A9C",
        "accent": "#F2C94C",
        "background": "#F7FBFC",
        "text": "#0B1B3A"
      }
    },
    "Alaska": {
      "inspiration": "Ice + Aurora",
      "colors": {
        "primary": "#0B3C49",
        "secondary": "#1C6E8C",
        "accent": "#7ED957",
        "background": "#F1F7F9",
        "text": "#081C24"
      }
    },
    "Arizona": {
      "inspiration": "Desert + Canyon",
      "colors": {
        "primary": "#8B3A2E",
        "secondary": "#C8553D",
        "accent": "#E09F3E",
        "background": "#FBF1E6",
        "text": "#2D1B12"
      }
    },
    "Arkansas": {
      "inspiration": "Forest + Springs",
      "colors": {
        "primary": "#1E5631",
        "secondary": "#4C956C",
        "accent": "#F4D35E",
        "background": "#F6FBF7",
        "text": "#102A22"
      }
    },
    "California": {
      "inspiration": "Coast + Urban",
      "colors": {
        "primary": "#1D3557",
        "secondary": "#457B9D",
        "accent": "#E63946",
        "background": "#F1FAEE",
        "text": "#0B132B"
      }
    },
    "Colorado": {
      "inspiration": "Mountains",
      "colors": {
        "primary": "#1F3C88",
        "secondary": "#5893D4",
        "accent": "#A9D6E5",
        "background": "#F5FAFF",
        "text": "#0B1B3A"
      }
    },
    "Connecticut": {
      "inspiration": "Coastal Classic",
      "colors": {
        "primary": "#243A5E",
        "secondary": "#5C7AEA",
        "accent": "#F4D160",
        "background": "#F6F8FC",
        "text": "#1C2541"
      }
    },
    "Delaware": {
      "inspiration": "Beach Calm",
      "colors": {
        "primary": "#005F73",
        "secondary": "#0A9396",
        "accent": "#E9D8A6",
        "background": "#F7FDFC",
        "text": "#001219"
      }
    },
    "Florida": {
      "inspiration": "Tropical",
      "colors": {
        "primary": "#006D77",
        "secondary": "#83C5BE",
        "accent": "#FFDDD2",
        "background": "#EDF6F9",
        "text": "#023047"
      }
    },
    "Georgia": {
      "inspiration": "Southern Charm",
      "colors": {
        "primary": "#264653",
        "secondary": "#2A9D8F",
        "accent": "#E9C46A",
        "background": "#F4F9F8",
        "text": "#1B2D2A"
      }
    },
    "Hawaii": {
      "inspiration": "Island Paradise",
      "colors": {
        "primary": "#005F99",
        "secondary": "#00B4D8",
        "accent": "#90DBF4",
        "background": "#F0FAFF",
        "text": "#012A4A"
      }
    },
    "Idaho": {
      "inspiration": "Alpine Nature",
      "colors": {
        "primary": "#2D6A4F",
        "secondary": "#40916C",
        "accent": "#B7E4C7",
        "background": "#F6FBF7",
        "text": "#102A22"
      }
    },
    "Illinois": {
      "inspiration": "Urban + Lake",
      "colors": {
        "primary": "#1F2937",
        "secondary": "#3B82F6",
        "accent": "#60A5FA",
        "background": "#F8FAFC",
        "text": "#020617"
      }
    },
    "Indiana": {
      "inspiration": "Midwest Balance",
      "colors": {
        "primary": "#2C3E50",
        "secondary": "#5DADE2",
        "accent": "#F4D03F",
        "background": "#F9FAFB",
        "text": "#1B2631"
      }
    },
    "Iowa": {
      "inspiration": "Countryside",
      "colors": {
        "primary": "#386641",
        "secondary": "#6A994E",
        "accent": "#F2E8CF",
        "background": "#FBFCF9",
        "text": "#1F2D16"
      }
    },
    "Kansas": {
      "inspiration": "Prairie",
      "colors": {
        "primary": "#5A3E2B",
        "secondary": "#A98467",
        "accent": "#F0EAD2",
        "background": "#FBF9F4",
        "text": "#2D1E12"
      }
    },
    "Kentucky": {
      "inspiration": "Heritage + Nature",
      "colors": {
        "primary": "#3A5A40",
        "secondary": "#588157",
        "accent": "#DDA15E",
        "background": "#F7FAF8",
        "text": "#1B2F24"
      }
    },
    "Louisiana": {
      "inspiration": "Jazz + Culture",
      "colors": {
        "primary": "#3A0CA3",
        "secondary": "#7209B7",
        "accent": "#F72585",
        "background": "#F9F7FD",
        "text": "#240046"
      }
    },
    "Maine": {
      "inspiration": "Rocky Coast",
      "colors": {
        "primary": "#1B4965",
        "secondary": "#5FA8D3",
        "accent": "#CAE9FF",
        "background": "#F4FAFF",
        "text": "#0B2545"
      }
    },
    "Maryland": {
      "inspiration": "Bay + History",
      "colors": {
        "primary": "#003049",
        "secondary": "#669BBC",
        "accent": "#F77F00",
        "background": "#F6F9FC",
        "text": "#1A1A1A"
      }
    },
    "Massachusetts": {
      "inspiration": "Colonial Coast",
      "colors": {
        "primary": "#1F2A44",
        "secondary": "#4A6FA5",
        "accent": "#F4A261",
        "background": "#F7F9FC",
        "text": "#0B132B"
      }
    },
    "Michigan": {
      "inspiration": "Lakes",
      "colors": {
        "primary": "#0B3C5D",
        "secondary": "#328CC1",
        "accent": "#D9B310",
        "background": "#F5F9FC",
        "text": "#1B1B1B"
      }
    },
    "Minnesota": {
      "inspiration": "North Woods",
      "colors": {
        "primary": "#1C3D5A",
        "secondary": "#4A90E2",
        "accent": "#A7C7E7",
        "background": "#F4F8FC",
        "text": "#0B1B3A"
      }
    },
    "Mississippi": {
      "inspiration": "River South",
      "colors": {
        "primary": "#5A2A27",
        "secondary": "#8C3A3A",
        "accent": "#E09F3E",
        "background": "#FBF4F3",
        "text": "#2B1A1A"
      }
    },
    "Missouri": {
      "inspiration": "Heartland",
      "colors": {
        "primary": "#3D405B",
        "secondary": "#81B29A",
        "accent": "#F2CC8F",
        "background": "#F7F8FA",
        "text": "#1C2541"
      }
    },
    "Montana": {
      "inspiration": "Big Sky",
      "colors": {
        "primary": "#1B4332",
        "secondary": "#40916C",
        "accent": "#A7C957",
        "background": "#F6FBF7",
        "text": "#102A22"
      }
    },
    "Nebraska": {
      "inspiration": "Plains",
      "colors": {
        "primary": "#6A4E42",
        "secondary": "#B08968",
        "accent": "#E6CCB2",
        "background": "#FBF7F3",
        "text": "#2E1F14"
      }
    },
    "Nevada": {
      "inspiration": "Desert + Neon",
      "colors": {
        "primary": "#2D1E2F",
        "secondary": "#7B2CBF",
        "accent": "#FFD166",
        "background": "#FAF7FF",
        "text": "#1A1025"
      }
    },
    "New Hampshire": {
      "inspiration": "Alpine Lakes",
      "colors": {
        "primary": "#2F3E46",
        "secondary": "#52796F",
        "accent": "#CAD2C5",
        "background": "#F6FAF8",
        "text": "#1B2D2A"
      }
    },
    "New Jersey": {
      "inspiration": "Shore + City",
      "colors": {
        "primary": "#003049",
        "secondary": "#669BBC",
        "accent": "#F77F00",
        "background": "#F6F9FC",
        "text": "#1A1A1A"
      }
    },
    "New Mexico": {
      "inspiration": "Southwest",
      "colors": {
        "primary": "#9B2226",
        "secondary": "#CA6702",
        "accent": "#E9D8A6",
        "background": "#FBF3E6",
        "text": "#3B1D1D"
      }
    },
    "New York": {
      "inspiration": "Urban Energy",
      "colors": {
        "primary": "#0B132B",
        "secondary": "#1C2541",
        "accent": "#E63946",
        "background": "#F8FAFC",
        "text": "#020617"
      }
    },
    "North Carolina": {
      "inspiration": "Mountains + Coast",
      "colors": {
        "primary": "#1B4965",
        "secondary": "#62B6CB",
        "accent": "#BEE9E8",
        "background": "#F4FAFB",
        "text": "#0B2545"
      }
    },
    "North Dakota": {
      "inspiration": "Prairie Calm",
      "colors": {
        "primary": "#344E41",
        "secondary": "#588157",
        "accent": "#A3B18A",
        "background": "#F6FBF8",
        "text": "#1B2F24"
      }
    },
    "Ohio": {
      "inspiration": "Modern Midwest",
      "colors": {
        "primary": "#22223B",
        "secondary": "#4A4E69",
        "accent": "#9A8C98",
        "background": "#F2E9E4",
        "text": "#1A1A1A"
      }
    },
    "Oklahoma": {
      "inspiration": "Plains + Route 66",
      "colors": {
        "primary": "#3D405B",
        "secondary": "#F4A261",
        "accent": "#E76F51",
        "background": "#F9F7F4",
        "text": "#1C2541"
      }
    },
    "Oregon": {
      "inspiration": "Forest + Coast",
      "colors": {
        "primary": "#2F5D50",
        "secondary": "#3A7D44",
        "accent": "#A3B18A",
        "background": "#F6FBF7",
        "text": "#102A22"
      }
    },
    "Pennsylvania": {
      "inspiration": "Historic",
      "colors": {
        "primary": "#2A2D34",
        "secondary": "#4A6FA5",
        "accent": "#F4A261",
        "background": "#F7F9FC",
        "text": "#1B2631"
      }
    },
    "Rhode Island": {
      "inspiration": "Nautical",
      "colors": {
        "primary": "#003566",
        "secondary": "#0077B6",
        "accent": "#CAF0F8",
        "background": "#F4FAFF",
        "text": "#001D3D"
      }
    },
    "South Carolina": {
      "inspiration": "Southern Coast",
      "colors": {
        "primary": "#264653",
        "secondary": "#2A9D8F",
        "accent": "#F4A261",
        "background": "#F7FBFA",
        "text": "#1B2D2A"
      }
    },
    "South Dakota": {
      "inspiration": "Badlands",
      "colors": {
        "primary": "#6A040F",
        "secondary": "#9D0208",
        "accent": "#E85D04",
        "background": "#FFF3E0",
        "text": "#2B0A0A"
      }
    },
    "Tennessee": {
      "inspiration": "Music + Mountains",
      "colors": {
        "primary": "#2D1E2F",
        "secondary": "#6A4C93",
        "accent": "#F4A261",
        "background": "#FAF7FD",
        "text": "#1A1025"
      }
    },
    "Texas": {
      "inspiration": "Bold + Vast",
      "colors": {
        "primary": "#1D3557",
        "secondary": "#E63946",
        "accent": "#F1FAEE",
        "background": "#F8FAFC",
        "text": "#0B132B"
      }
    },
    "Utah": {
      "inspiration": "Red Rock",
      "colors": {
        "primary": "#9B2226",
        "secondary": "#BB3E03",
        "accent": "#E9D8A6",
        "background": "#FBF2E8",
        "text": "#3B1D1D"
      }
    },
    "Vermont": {
      "inspiration": "Green Mountains",
      "colors": {
        "primary": "#2D6A4F",
        "secondary": "#74C69D",
        "accent": "#D8F3DC",
        "background": "#F6FBF7",
        "text": "#102A22"
      }
    },
    "Virginia": {
      "inspiration": "Colonial Coast",
      "colors": {
        "primary": "#003049",
        "secondary": "#669BBC",
        "accent": "#F4D35E",
        "background": "#F6F9FC",
        "text": "#1A1A1A"
      }
    },
    "Washington": {
      "inspiration": "Evergreen",
      "colors": {
        "primary": "#1B4332",
        "secondary": "#2D6A4F",
        "accent": "#95D5B2",
        "background": "#F4FAF6",
        "text": "#102A22"
      }
    },
    "West Virginia": {
      "inspiration": "Rugged Nature",
      "colors": {
        "primary": "#283618",
        "secondary": "#606C38",
        "accent": "#DDA15E",
        "background": "#F7F9F4",
        "text": "#1B2F24"
      }
    },
    "Wisconsin": {
      "inspiration": "Lakes + Forest",
      "colors": {
        "primary": "#003049",
        "secondary": "#669BBC",
        "accent": "#A3CEF1",
        "background": "#F6FAFD",
        "text": "#1A1A1A"
      }
    },
    "Wyoming": {
      "inspiration": "Wild West",
      "colors": {
        "primary": "#3A5A40",
        "secondary": "#588157",
        "accent": "#DDA15E",
        "background": "#F7FAF8",
        "text": "#1B2F24"
      }
    }
  };
  
  // Apply to your existing CSS variables used in :root
  function applyStateTheme(stateName) {
    const theme = STATE_THEMES[stateName];
    if (!theme) return;
  
    const c = theme.colors;
    const root = document.documentElement.style;
  
    // your UI uses these heavily (gradient buttons, focus rings, etc.)
    root.setProperty("--brandA", c.primary);
    root.setProperty("--brandB", c.secondary);
  
    // keep existing structure, just adapt palette
    root.setProperty("--muted", hexToRgba(c.text, 0.55));
    root.setProperty("--stroke", hexToRgba(c.secondary, 0.45));
  }
  
  // helper
  function hexToRgba(hex, a) {
    const h = hex.replace("#", "");
    const r = parseInt(h.slice(0, 2), 16);
    const g = parseInt(h.slice(2, 4), 16);
    const b = parseInt(h.slice(4, 6), 16);
    return `rgba(${r},${g},${b},${a})`;
  }