# Contractor component library

Open `/style-guide/` on the local preview (`./jdd.sh`, port 1317), or use **Component guide** in the preview footer. The catalogue renders the actual partials and current theme. It includes twenty-four contractor components, six existing patterns, four foundations, and a map of the shell and workflow components that need their own page context: 34 specimens in total.

The field-office edition continues the existing parody: Jeff treats doors with unreasonable emotional seriousness, Doreen restores the conversation to practical matters, and Lenny remains a level. That voice lives in the example data, not the component behavior. Fictional staff, testimonials, packages, and project events stay visibly fictional. Real credentials, prices, approvals, and installation details are not invented to support the joke.

## Source map

| Source | Responsibility |
| --- | --- |
| `layouts/partials/components/` | Twenty-four reusable, data-driven contractor partials plus the shared choice-script loader |
| `assets/scss/_contractor.scss` | Namespaced component styling, responsive layout, forced-colors treatment |
| `data/component_library.json` | Review-only catalogue metadata and explicit example content |
| `data/site_components.json` | Visitor-page copy, page references, and optional feature gates; registered in publication core sources |
| `layouts/partials/site-component.html` | Allowed component dispatch, section headings, unique instance prefixes, feature gates, choice-script demand |
| `content/style-guide.md` | Review-only/noindex route |
| `layouts/_default/style-guide.html` | Live specimens, usage snippets, data contracts, library map |
| `layouts/partials/style-guide/` | Four theme foundation specimens |
| `assets/scss/_style-guide.scss` | Catalogue layout, contained legacy examples, and responsive chrome |
| `assets/js/style-guide.js` | Guide-only search, family filter, fragment recovery, and clipboard enhancement |
| `assets/js/contractor-choices.js` | Repeatable, isolated radio-to-panel behavior for project and finish choices |
| `layouts/partials/easter-egg.html`, `assets/scss/_easter-eggs.scss` | Jeff-profile native disclosures and quiet presentation |

## Reuse a contractor component

### Where the site uses them

All twenty-four contractor components have an actual page placement across twelve visitor routes. Each catalogue specimen includes a **See it on the site** link when its destination and feature are enabled. The six project-paperwork patterns use short, independent page copy; the guide remains a separate set of examples.

| Page | Components | Purpose |
| --- | --- | --- |
| Home | Project chooser | Route a new installation, replacement, or movement problem to the right service |
| Barn-door installation | Scope panel, responsibility matrix, project timeline | Name supply, access and finishing responsibilities before agreeing work |
| Barn-door replacement | Material comparison, decision register | Compare design directions and record reuse and finish decisions still to resolve |
| Tracks & hardware | Service card, material schedule | Gather compatible product references and establish supply responsibilities |
| Barn-door adjustments | Punch list, follow-up plan | Record unresolved items, then discuss care and contact arrangements |
| Gallery | Finish selector, project story | Explore clearly labelled illustrations and a fictional design study |
| About | Crew roster, field notes, credential list | Introduce the parody cast and keep real qualification status explicit |
| Pricing | Package comparison, cost drivers, change summary | Explain scope choices and what a revised agreement needs |
| Contact | Visit checklist, site-access plan | Prepare details and discuss access needs after the existing brief form |
| Service Area | Availability panel | Keep coverage and timing unconfirmed until discussed directly |
| FAQ | Handover pack, document register | Collect walkthrough questions and link to the survey while identifying paperwork still needed |
| Reviews | Featured testimonial | Present an explicitly fictional quote and Doreen’s reply |

The homepage chooser replaces the earlier repeated consultation-question panel. About uses the new roster in place of the old image cards, and the new credential list in place of its legacy credential block. Existing inquiry and gallery implementations remain single instances.

For a visitor-page placement, add a record to `data/site_components.json` with `component`, `page` (a Hugo content path), `eyebrow`, `heading`, `content`, and optionally `feature`. Then call:

```go-html-template
{{ partial "site-component.html" (dict "page" . "key" "home-start") }}
```

Keep each key unique within a page. The wrapper supplies an `h2` and prefixes component IDs with `site-`. Missing content and unknown component types fail the build. Page visibility still comes from the existing `page-disabled.html` guard; About’s crew/notes also honor `team`, and its evidence list honors `credentials`. The `page` field lets the guide resolve links with Hugo’s real permalink rather than hardcoding a deployment prefix.

`baseof.html` loads the shared choice script once after rendering a page that requested it through the wrapper. Currently those visitor routes are Home and Gallery. The guide retains its independent script deduplication. Guide scripts never load on visitor pages. Components use independent page copy; editing or removing catalogue samples does not alter their visitor-page content.

`data/site_components.json` is registered in `data/publishing.json` under `core`, so the existing Python and Hugo publication guards both include it in revision-bound review. This registration is not an approval. New copy retains explicit parody/provenance labels and unresolved business inputs.

### Direct partial calls

All twenty-four components receive a dictionary containing `id` and `content`. Supply a unique HTML-id-safe prefix for each instance. IDs connect headings, labels, hints, radio-group names, and panels, including when two instances appear on the same page. All visible content is escaped by Hugo; partials do not apply `safeHTML` to supplied text.

```go-html-template
{{ partial "components/scope-panel.html" (dict
  "id" "kitchen-scope"
  "content" .Params.projectScope
) }}
```

An example page front matter object:

```yaml
projectScope:
  title: "Discuss the proposed work"
  intro: "Example discussion outline; confirm the actual scope."
  groups:
    - title: "To discuss"
      items:
        - "Who supplies the materials"
        - "Access and timing constraints"
  note: "The written proposal determines the agreed scope."
```

Use page front matter or an owner-reviewed production dataset for real content. The guide's fixture is deliberately illustrative and must not become a source of business claims. If introducing a production dataset, add it to the existing publication source/evidence contract; do not assume a new file under `data/` is automatically covered. The current guide fixture is used only by the review page.

| Partial | Content fields | Intended use |
| --- | --- | --- |
| `service-card.html` | `title`, `body`, `points[]`; optional `eyebrow`, `href`, `action` | One service with an optional next step |
| `project-story.html` | `title`, `image`, `alt`, `caption`, `label`, `facts[{label,value}]`, `challenge`, `approach` | Brief and approach with visible image provenance |
| `scope-panel.html` | `title`, `intro`, `groups[{title,items[]}]`; optional `note` | Proposed scope, exclusions, responsibilities, open questions |
| `project-timeline.html` | `title`, `intro`, `steps[{title,body,state}]`; optional `note` | Complete/current/upcoming steps, with explicit text labels |
| `material-comparison.html` | `title`, `intro`, `rows[{name,character,care,confirm}]`; optional `note` | Planning comparison with a caption and row/column headers |
| `cost-drivers.html` | `title`, `intro`, `items[{title,body}]`, `note` | Explain proposal inputs without estimating a price |
| `visit-checklist.html` | `title`, `intro`, `legend`, `items[]`, `note` | Native, local preparation checkboxes |
| `credential-list.html` | `title`, `intro`, `items[{title,detail,status}]` | Evidence status without automatic verification claims |
| `availability-panel.html` | `title`, `status`, `body`, `note`; optional `areas[]`, `href`, `action` | Explicit coverage/timing status and empty state |
| `handover-pack.html` | `title`, `intro`, `groups[{title,body,items[]}]`, `note` | Native disclosures for walkthrough, care, and support references |
| `project-chooser.html` | `eyebrow`, `title`, `intro`, `legend`, `options[{label,summary,title,body,href?,action?}]`, `note` | Starting-point choice with matching preparation guidance |
| `finish-selector.html` | `eyebrow`, `title`, `intro`, `legend`, `options[{label,description,image,alt,caption}]`, `note` | Illustrated design choices with a shared radio group |
| `package-comparison.html` | `eyebrow`, `title`, `intro`, `packages[{label,title,body,items[],footer}]`, `note` | Compare scope groupings without inventing prices |
| `crew-roster.html` | `eyebrow`, `title`, `intro`, `people[{initials,name,role,bio,aside}]`, `note` | Responsibility and biography rows with decorative initials |
| `featured-testimonial.html` | `eyebrow`, `title`, `quote`, `name`, `context`, `replyLabel`, `reply`, `disclosure` | Attributed quote and reply with visible provenance |
| `field-notes.html` | `eyebrow`, `title`, `intro`, `entries[{label,title,body,author}]`, `note` | Editorial observations and authorship |
| `change-summary.html` | `eyebrow`, `title`, `reference`, `status`, `intro`, `original:{label,body}`, `requested:{label,body}`, `impacts[{label,value}]`, `note` | Read-only proposed change and unresolved impacts |
| `follow-up-plan.html` | `eyebrow`, `title`, `intro`, `items[{when,title,body,owner}]`, `boundary`, `note` | Follow-up topics, responsibility, and contact boundaries |
| `decision-register.html` | `eyebrow`, `title`, `intro`, `entries[{reference,title,status,decision,reason,next}]`, `note` | Preserve a decision discussion, reason and next step |
| `responsibility-matrix.html` | `eyebrow`, `title`, `intro`, `rows[{task,owner,coordination,status}]`, `note` | Proposed ownership and coordination in a labelled table |
| `site-access-plan.html` | `eyebrow`, `title`, `intro`, `arrival:{label,body}`, `areas[{title,detail,confirm}]`, `note` | Public planning prompts for arrival, routes and use of the space |
| `material-schedule.html` | `eyebrow`, `title`, `intro`, `rows[{item,selection,responsibility,status}]`, `note` | Proposed products, supply responsibility and unresolved states |
| `punch-list.html` | `eyebrow`, `title`, `intro`, `items[{reference,title,status,observation,owner,next}]`, `note` | Read-only observations and follow-up actions |
| `document-register.html` | `eyebrow`, `title`, `intro`, `documents[{title,kind,status,detail,href?,action?}]`, `note` | Real resource links alongside missing-document states |

Use at most one `current` timeline step. Unknown state strings render as upcoming. Availability does not perform a postcode lookup, reserve a visit, or calculate a response time. Credential statuses are editorial input, not a validation system. Actions render only when both `href` and `action` are present; use site-relative paths without a leading slash so Hugo retains deployment subpaths.

Components use `h3` headings beneath catalogue `h2` headings. Place them under a section heading in real layouts, or adapt their heading level intentionally. The guide shows the current token colors rather than copying hex values into the stylesheet. It uses the site's existing Jost/Newsreader font stacks and fallbacks.

### Choice component enhancement

Include the shared loader once, after every project chooser or finish selector on that page:

```go-html-template
{{ partial "components/project-chooser.html" (dict "id" "project-start" "content" .Params.projectStart) }}
{{ partial "components/finish-selector.html" (dict "id" "finish-ideas" "content" .Params.finishIdeas) }}
{{ partial "components/choice-script.html" . }}
```

The guide reads optional `script` declarations in its catalogue and loads each unique helper once. Its usage snippets include the helper. The script binds each instance independently and safely ignores an accidental second load. It validates the input/panel mapping before hiding any fallback content; a malformed instance keeps its option content readable while other instances can still initialize.

Use distinct text labels for every option. Native radios preserve keyboard behavior, visible focus, and checked-state semantics. A choice reveals one existing panel and announces its label; it does not interpret text as HTML. Browser-restored selections are honored. Without JavaScript, the inactive controls stay hidden and all option panels are visible. The script makes no network or storage calls. Finish photographs represent different illustrated designs, not exact recolors of a product or a guarantee of appearance.

## Interaction and boundaries

- All specimens render without JavaScript. Filter controls stay hidden until initialization; native disclosures and checkboxes remain usable. Gallery image links retain the existing no-JavaScript fallback.
- Search matches all entered words against the title, purpose, contract, and example data, in combination with the selected family. Character searches such as “Lenny” find the relevant specimens. Clearing filters restores all specimens. Following a component fragment reveals a filtered-out specimen, including when the current fragment is clicked again.
- Clipboard buttons appear only when the browser exposes the Clipboard API. A rejected copy focuses and selects the snippet for manual copying, and announces that copying did not succeed.
- The preparation checklist neither sends nor stores data. Browsers may restore native form values. It is not a survey packet or completion record.
- The guide intentionally includes one instance of the existing gallery because its initializer binds to one grid/dialog. Existing inquiry, intake, and survey tools are linked in context rather than cloned into the catalogue.
- `reviewOnly: true` reuses `page-disabled.html`. Outside review mode the guide is replaced by neutral noindex unavailable content and its script is not loaded. Its own `noindex` also excludes it from site search and sitemap. Review/noindex does not provide privacy.
- No price, license, insurance, service territory, appointment, performance specification, customer quote, or completion acceptance is established by a specimen.

## Project-paperwork patterns

The six October 13 additions fill gaps between discussing scope and recording open items. They remain read-only specimens: the decision register does not approve a choice, the responsibility matrix does not assign work, and the punch list does not accept an installation. Status is explicit supplied text. The material schedule performs no stock, pricing, compatibility or purchasing operation. No dates, quantities, approvals or appointments are inferred.

The site-access plan is for public planning prompts. Never put private access codes, keys, alarm instructions or customer records into the public dataset. The document register is a resource index, not an upload/store; an action appears only when both `href` and `action` are supplied. Its guide example links to the real survey and FAQ routes, while missing product instructions and agreements have no fake download buttons.

Responsibility and material tables retain captions, scoped headers and labelled keyboard-focusable scroll regions. Records and access cards stack at narrow widths. All six use the existing component variables and heading hierarchy and need no additional JavaScript. Give every instance a unique `id`, including table hint references.

Owner-run coverage repeats each new pattern, supplies hostile text, checks read-only markup and table semantics, checks document-link omission and subpaths, and renders all six through the real site wrapper in an isolated fixture. That coverage has been authored, not executed by the agent.

The October 13 browser pass found no page overflow for the new previews at 320px, checked the document register at 320px and the site-access grid at 1440px, and confirmed keyboard scrolling and catalogue search/reset. The 34-specimen guide had no duplicate IDs at 390px. The staging compilation and source/artifact audits passed; see [verification](verification.md) for the scope and remaining checks.

## Quiet character notes

`layouts/partials/easter-egg.html` renders an optional native disclosure from `id`, `label`, and `lines[]`, with an optional decorative `level`. It is specific to the Jeff profile. All text is escaped; it has no script, storage, timer, animation, or announcement region. The disclosure starts closed and retains the native marker, keyboard behavior, and visible focus, with a minimum 44px summary target.

There are three placements: Lenny in the homepage footer, Jeff after the Gallery grid, and Doreen after About’s fictional field notes. Crew notes respect the `team` flag; Gallery respects its page flag. These do not appear in the contact form, survey workspace, urgent-help page, or error recovery. The partial and stylesheet are automatically included in the existing publication source inventory. Keep future jokes out of field labels, validation, delivery receipts, and factual product guidance.

Owner-run coverage in `test_site_components.py` checks the limited placements, closed native disclosure markup, utility-page absence, and feature suppression. It was authored but not run by the agent. For a browser check, tab to each summary and open/close it with Enter or Space; repeat at 320px and with JavaScript disabled. Only the note should expand, without navigation, focus movement, or a saved preference.

Local browser spot check (2026-10-12): all three notes began closed and had 44px summary targets. Home was inspected at 390px; Gallery and About at 320px. Enter and Space opened/closed the Home and Gallery notes while focus remained on their summaries; About opened with Enter. The notes fit these viewports. No-JavaScript and assistive-technology behavior were not separately exercised; the interaction uses native HTML without a script.

## Owner-run verification

Regressions are in `tests/style-guide.test.cjs`, `tests/contractor-choices.test.cjs`, `tests/test_component_library.py`, and `tests/test_site_components.py`; the existing verification script discovers them automatically. They cover filtering and reset behavior, direct links, clipboard failure, repeated-instance IDs and radio names, escaped content, subpath links, review visibility, choice isolation, restored selections, malformed-instance fallback, repeat loading, and catalogue output. The site integration coverage adds page placement, heading references, feature suppression, selective script loading, catalogue independence, retained gallery/form instances, and publication source registration. They do not establish browser/assistive-technology acceptance or business approval.

Ryan reported nine Python component-library tests and nine JavaScript choice tests passing before the visitor-page integration. This integration has a successful staging compilation; its new regression coverage is authored but has not been run by the agent. For a focused owner run (requires the existing Python dependencies):

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*component*.py'
```

For the full owner-controlled verification:

```sh
bash scripts/verify-local.sh
```

For a visual review, visit `/style-guide/` using the regular local preview. Check a narrow viewport and increased text size; tab through filters, checkboxes, disclosures, table scrolling, and the gallery. Inspect the no-JavaScript fallback and reduced-motion/forced-colors behavior with the actual browser and assistive technology used. These are review steps, not completed validation claims.

## Visual integration pass — 2026-10-12

Reviewed the running local Hugo preview in Chrome with device emulation. All twelve integrated visitor routes were inspected at a 320px viewport for page width and clipped heading/control bounds. Each route also received a visual spot check at 320px or 390px. Home, Gallery, and Pricing received additional desktop/tablet inspection at 768px or 1440px. The guide's chooser specimen was checked at 320px after the shared styles changed.

The pass corrected the mobile homepage's header/headline overlap. The mobile announcement and header now occupy normal document flow, and the header can wrap as text grows. The conflicting hero-order rules were removed from the survey stylesheet; the modern theme now owns that layout. The mobile menu uses the opaque espresso theme surface instead of the old translucent green.

Component sections now use architectural uppercase headings, serif subheadings, quieter rules, and the site's image treatment. Visitor-page cards lose their redundant outer padding on mobile; standalone guide specimens retain their own card surface. The enhanced desktop chooser places options beside the selected guidance. Finish options become equal full-width controls below 480px, while desktop/tablet finish images sit beside their captions. Timeline gutters, notes, roster columns, and fact lists give narrow screens more usable text width. Seven long section headings were shortened while retaining the parody.

Observed browser checks:

- All twelve integrated routes had matching document/viewport width at 320px; the inspected heading, paragraph, label, input, select, and button bounds stayed within the viewport, excluding intentional scroll regions.
- The material comparison scrolled to its last column inside its own region without widening the page.
- Arrow keys selected the matching Home/Gallery panels and updated their status text. The Home action received keyboard focus above the fixed message bar; the Gallery option showed its focus outline.
- The mobile menu opened by keyboard and retained an internally scrollable list above the message bar. Its background no longer showed the headline through the panel.
- A 200% root-font-size simulation on the 390px homepage initially exposed overflowing legacy headings, labels, and swatches. After repairs, the layout, window, and document widths were all 390px, with no non-scroll-region overflow found inside main content. The header remained above the headline with the announcement visible and in a separately inspected hidden-announcement state. This is a CSS text-enlargement spot check, not a claim of full browser zoom or assistive-technology acceptance.

Repeatable visual regression coverage for future changes:

1. In a fresh preview context, inspect Home with the announcement visible, then dismissed. At 320px and 390px, the logo/menu and headline must not overlap. Enlarge text and confirm the header can wrap.
2. At 320px, visit the twelve placements in the table above. Look for clipped text and controls, unintended page scrolling, and cramped nested padding. Scroll the material comparison independently.
3. At 390px, use arrow keys on Home and Gallery choices, then tab to the next control. The selected panel, checked radio, status text, and visible focus must agree.
4. At 768px and 1440px, inspect Home, Gallery, and Pricing. The chooser's two columns, finish image/caption, and comparison cards must remain readable and aligned.
5. Open the FAQ handover disclosures and Contact checklist; inspect the About roster, field notes, and credential statuses. Check the fixed message bar does not obscure focused controls.
6. Inspect the guide's standalone specimens, then repeat with JavaScript disabled and with the actual zoom, forced-colors, reduced-motion, and assistive-technology settings used. Those latter environment checks remain owner review items.

The browser pass does not establish real-device, screen-reader, cross-browser, business, or publication acceptance. Automated suites were not run for this visual pass; use the owner-run command above when ready.

## Copy pass — 2026-10-12

Tightened the visitor pages, service summaries and FAQs, shared prompts, and the component examples. Each service now has its own character beat; repeated “Jeff will” endings and repeated preparation instructions were cut. Jeff supplies the door obsession, Doreen makes decisions and protects her time, and Lenny remains a silent four-foot level. The guide keeps distinct specimen stories rather than copying visitor-page prose.

Practical form labels, survey instructions, data contracts, and interaction scripts retain their existing meaning. Fictional reviews are identified where they appear. Older booking, coverage, payment, credential, and return-visit copy now agrees with the preview’s unconfirmed business details. None of these editorial changes supplies business evidence or approval.

The staging build succeeded. Browser spot checks of the revised Home, About crew, and Pricing copy at 390px and the installation page at 320px showed readable text within the viewport. This was an editorial check, not a repeat of the full visual review above. Automated suites were not run; the owner verification command remains `bash scripts/verify-local.sh`.

## Final source and documentation review — 2026-10-13

The review found that older FAQ clearance answers still prescribed universal dimensions. They now reference the four entries in `data/door-guidance.json`, shared with the measuring cards. Brief help, Contact and the delivery FAQ resolve the existing delivery-status partial so the wording follows local-only, direct-contact or optional online configuration. The FAQ source validator now accepts those supported answer sources and rejects malformed flags, empty answers and unknown guidance references.

Regression coverage was added for the shared guidance, configured delivery wording and policy alternatives. It has not been run by the agent. The generated feature menu was corrected at its source to distinguish disabled-page shells from omitted drafts. The README, roadmap and affected documents were reconciled with this state; earlier test receipts remain historical. See [verification](verification.md) for current checks and remaining acceptance.


## Project-paperwork visitor integration — 2026-10-13

All six paperwork patterns now have the placements listed above. Installation names proposed responsibilities; replacement keeps reuse and finish decisions open; hardware groups product references; adjustments shows explicitly fictional unresolved items before the follow-up plan. Contact keeps its form first and uses two short access-planning areas. FAQ links to the real survey while leaving missing manufacturer instructions and scope documents as labelled text.

The existing mobile styles handle these placements: record facts and statuses stack, access areas become one column, document labels wrap, and the two tables scroll inside focusable regions. The six affected routes received visual and width checks at 320px; installation and Contact received 1440px visual checks. The hardware table responded to ArrowRight while focused. No additional script or page-specific stylesheet was needed. See [verification](verification.md) for the current evidence boundary and owner-run regression command.

## Keyboard and zoom follow-up — 2026-10-13

Native Chrome 200% and 400% zoom checks now cover the six paperwork specimens and their visitor placements. Guide disclosures and placement links worked by keyboard. Both guide and visitor tables accepted arrow-key scrolling and Tab exit; Shift+Tab return was also checked in the guide. The document register links to the actual survey.

The status columns have a 9rem minimum width to avoid splitting ordinary words. The shared Message bar moves into normal flow when the viewport is at most 700px wide and 480px high; taller phone views reserve scroll clearance above the fixed bar. This corrects a partially obscured focus outline found at 400%. See [verification](verification.md) for measurements, the repeatable manual regression checklist and checks still outstanding.
