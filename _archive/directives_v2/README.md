# Директивы конвейера, версия 2 (10–15.09.2026)

Здесь лежат директивы `NN_directive_*.md`, по которым собран DesignStack. 15.09.2026 они
перенесены в навыки `.claude/skills/<имя>/SKILL.md`: содержание то же, но навык поднимается
по описанию, а не по команде `/directive NN`, которой больше нет. Файлы оставлены, чтобы
можно было свериться с исходником и откатиться.

| Было | Стало | Этап |
|---|---|---|
| `02_directive_briefing.md` | `.claude/skills/briefing/` | 02 |
| `03_directive_research.md` | `.claude/skills/competitor-research/` | 03 |
| `04_directive_personas.md` | `.claude/skills/personas/` | 04 |
| `05_directive_interview.md` | `.claude/skills/persona-interview/` | 05 |
| `06_directive_spec.md` | `.claude/skills/product-spec/` | 06 |
| `07_directive_sitemap.md` | `.claude/skills/sitemap/` | 07 |
| `08_directive_wireframes.md` | `.claude/skills/wireframes/` | 08 |
| `09_directive_brand.md` | `.claude/skills/brand/` | 09 |
| `10_directive_tokens.md` | `.claude/skills/design-tokens/` | 10 |
| `11_directive_patterns.md` | `.claude/skills/patterns-library/` | 11 |
| `12_directive_core_plugin.md` | `.claude/skills/core-plugin/` | 12 |
| `13_directive_templates.md` | `.claude/skills/page-templates/` | 13 |
| `14_directive_behavior.md` | `.claude/skills/site-behavior/` | 14 |
| `15_directive_site_audit.md` | `.claude/skills/site-audit/` | 15 |
| `16_directive_content.md` | `.claude/skills/catalog-content/` | 16 |
| `17_directive_seo_analytics.md` | `.claude/skills/seo-analytics/` | 17 |
| `18_directive_repo.md` | `.claude/skills/repo/` | 18 |
| `19_directive_deploy.md` | `.claude/skills/deploy/` | 19 |
| `30_directive_release_environment.md` | `.claude/skills/ai-environment/` | — |

Навык-переходник `directive`, который запускал этап по номеру, лежит в `_archive/skills_v1/`.
Номера этапов живут дальше: в карте `00_pipeline.md` и в журнале `docs/DECISIONS.md`.

Первая версия конвейера — под приложение, с Figma и React — в `_archive/directives_v1/`.
