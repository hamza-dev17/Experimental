# Experimental HTML Projects

A collection of fun, experimental, single-file HTML projects focused on visuals, interaction, and realtime effects.


## Projects

| Project | Description | Link |
|---|---|---|
| Burst | Hand-tracking particles with constellation behavior and fist-driven geometry mode. | `projects/burst/index.html` |
| Hidden Image | Camera motion refracts a fluid field to reveal a hidden image. | `projects/hidden-image/index.html` |
| Liquid | Fluid mirror simulation that reacts to webcam motion. | `projects/liquid/index.html` |
| Tear | Two-hand portal effect with bloom lighting and gesture-based expansion. | `projects/tear/index.html` |

## Repository Structure

```text
.
├── CONTRIBUTING.md
├── index.html
├── README.md
└── projects
    ├── _template
    │   ├── index.html
    │   └── README.md
    ├── burst
    │   ├── index.html
    │   └── README.md
    ├── hidden-image
    │   ├── index.html
    │   └── README.md
    ├── liquid
    │   ├── index.html
    │   └── README.md
    └── tear
        ├── index.html
        └── README.md
```

## Adding New Projects

- Start from `projects/_template`.
- Follow the checklist in `CONTRIBUTING.md`.
- Keep project folders in lowercase kebab-case.

## Notes

- Most projects require camera permission.
- External libraries are loaded from CDNs.
- These projects are intentionally experimental and may prioritize visual exploration over production hardening.
