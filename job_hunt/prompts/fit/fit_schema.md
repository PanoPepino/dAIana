{
  "type": "object",
  "properties": {
    "company_values": { "type": "array", "items": { "type": "string" } },
    "job_character": {
      "type": "object",
      "properties": {
        "working_style":       { "type": "string" },
        "thinking_style":      { "type": "string" },
        "team_collaboration":  { "type": "string" },
        "stakeholder_relations": { "type": "string" }
      },
      "required": ["working_style", "thinking_style", "team_collaboration", "stakeholder_relations"]
    },
    "top_concepts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "why":   { "type": "string" }
        },
        "required": ["label", "why"]
      }
    },
    "riasec_fit": {
      "type": "object",
      "properties": {
        "investigative": { "type": "object", "properties": { "level": { "type": "string" }, "evidence": { "type": "string" } }, "required": ["level", "evidence"] },
        "artistic":      { "type": "object", "properties": { "level": { "type": "string" }, "evidence": { "type": "string" } }, "required": ["level", "evidence"] },
        "enterprising":  { "type": "object", "properties": { "level": { "type": "string" }, "evidence": { "type": "string" } }, "required": ["level", "evidence"] },
        "conventional":  { "type": "object", "properties": { "level": { "type": "string" }, "evidence": { "type": "string" } }, "required": ["level", "evidence"] },
        "social":        { "type": "object", "properties": { "level": { "type": "string" }, "evidence": { "type": "string" } }, "required": ["level", "evidence"] }
      },
      "required": ["investigative", "artistic", "enterprising", "conventional", "social"]
    },
    "overall": {
      "type": "object",
      "properties": {
        "fit_score":  { "type": "integer" },
        "fit":        { "type": "string" },
        "blind_spot": { "type": "string" }
      },
      "required": ["fit_score", "fit", "blind_spot"]
    }
  },
  "required": ["company_values", "job_character", "top_concepts", "riasec_fit", "overall"]
}
