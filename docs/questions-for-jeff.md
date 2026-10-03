# Questions for Jeff — Site Launch Intake

This intake document collects the business facts, policies, and media required to transition **Jeff Does Doors** from the current illustrative preview draft to an owner-approved, production-ready website.

---

## 1. Core Services & Scope of Work

The website currently proposes four core service categories. We need to confirm exactly what Jeff does and does not offer.

### 1.1 Door Supply & Fabrication
- [ ] **Do you build custom doors from scratch, install pre-made/customer-purchased doors, or both?**
  - *Option A*: Custom build and fabrication only.
  - *Option B*: Installation and fitting of customer-supplied doors only.
  - *Option C*: Both (custom fabrication upon request, plus professional installation of supplied doors).
- [ ] **What wood species and door styles do you prefer or specialize in?**
  - *(e.g., White oak, walnut, knotty pine, reclaimed timber, modern slab, British brace / X-brace, paneled, glass/steel frames)*
- [ ] **Do you supply the tracks, rollers, and handles, or does the homeowner choose/order them?**

The guidance now asks for the selected door/hardware instructions and actual site conditions rather than prescribing a timber species, header, soft-close system or guide for every job.

- [ ] Which slab and hardware systems do you use or accept?
- [ ] Who verifies the wall structure, mounting method and product compatibility?
- [ ] Which finishing, adjustment, soft-close and guide work do you provide?
- [ ] What belongs in your survey, installation checks and customer handover?

### 1.2 Upgrades, Conversions & Repairs
- [ ] **Swing-to-Slide Conversions**: Do you take on projects replacing standard swinging doors with barn-style doors? Do you handle the drywall patching, trim casing, or painting required when an old jamb is removed?
- [ ] **Door Adjustments & Tune-Ups**: Do you take service calls for existing barn doors that rub, squeak, or come off their guides?
- [ ] **Clear Exclusions**: What do you **NOT** do?
  - *(e.g., Exterior entrance doors, agricultural barn doors, pocket doors, electrical/automatic openers)*

---

## 2. Contact Details & Customer Response

The preview site currently has phone, email, and hours suppressed to prevent bogus inquiries.

- [ ] **Primary Phone Number**: 
  - *Can this number receive SMS / text messages for project photos?* [ ] Yes [ ] No
- [ ] **Primary Email Address**:
- [ ] **Response Expectation**: What can customers realistically expect when reaching out?
  - *(e.g., "Replies within 1 business day", "Calls returned by evening")*
- [ ] **Operating Hours**:
  - Monday – Friday:
  - Saturday:
  - Sunday:
  - *By appointment only?* [ ] Yes [ ] No
- [ ] **Business Address Privacy**:
  - Is your business address a public workshop/showroom that customers visit?
  - *Or is it a private home/shop where you travel to the customer?* *(Recommended: hide street address and show service area only)*

---

## 3. Service Territory & Geography

The site needs a confirmed service territory to display on the homepage and `/service-area`.

- [ ] **Base Location**: City, State, and Zip Code.
- [ ] **Primary Coverage Area**: Which towns, cities, or counties do you regularly serve?
  - City / Town list:
  - County list:
- [ ] **Travel Radius**: Maximum travel distance from your base (e.g., 25 miles, 45 minutes)?
- [ ] **Travel Policy**: Do you charge a travel consultation fee for projects outside your primary zone?

---

## 4. "About Jeff" & Story Content

The `/about` page currently explains the design direction and features workshop imagery, but needs Jeff's real background.

- [ ] **How long have you been doing door work or fine carpentry?**
- [ ] **What led you to specialize specifically in barn-style doors?**
- [ ] **What is your working philosophy or standard of work?**
  - *(e.g., "A door should slide with one finger", "Every opening deserves character", "Clean job sites and respect for your home")*
- [ ] **Do you want a photo of yourself on the site, or do you prefer the focus strictly on the doors and workshop tools?**

---

## 5. Real Job Photography & Proof

The site currently uses 9 high-resolution AI-generated illustrative WebP concepts clearly labeled as placeholders. To launch, we should replace as many as possible with real work.

- [ ] **Job Photos**: Can you provide 4 to 8 high-resolution photos of doors you have installed or built?
  - *Ideally:*
    - Full straight-on view of the door and doorway opening.
    - Close-up of the overhead track, rollers, and mounting beam.
    - Close-up of the handle, pull, or bottom floor guide.
    - Wide shot showing how the door looks in the room.
- [ ] **Photo Permissions**: Do you have the homeowner's consent to display these photos online?
- [ ] **Client Testimonials / Reviews**:
  - Do you have 2–4 quotes or Google reviews from happy clients we can feature?
  - *(Need: Quote text, client first name, city/neighborhood)*

---

## 6. Pricing & Inquiry Process

- [ ] **Pricing Transparency**: Do you want ballpark price ranges displayed on the site, or should all projects be custom estimates based on the opening?
- [ ] **Estimating Steps**: What should homeowners have ready before contacting you?
  - Width and height of opening?
  - Wall space available to the left or right for the door to slide open?
  - Photos of the current opening?
  - Inspiration pictures or preferred finish?

---

## 7. Domain & Online Setup

- [ ] **Website Domain**: What domain do you own or want to use? *(e.g., `jeffdoesdoors.com`)*
- [ ] **Google Business Profile**: Do you have an existing Google Business / Google Maps listing? If so, what is the exact business name on the listing?
- [ ] **Social Media**: Do you have an active Instagram, Facebook, or Pinterest page you want linked?
- [ ] **Online Intake**: Do you want customers to contact you via direct phone/email, or do you want an online message builder that submits directly to your inbox?

---

## Next Steps Once Returned

1. Update `profiles/jeff-does-doors.toml` with confirmed phone, email, hours, and service territory.
2. Update `data/services.yaml` and `content/about.md` with Jeff's authentic copy and scope.
3. Confirm the four *Craft standards* practices above, then remove the review-mode "Proposed" flag from `layouts/partials/craft-standards.html` or drop the section.
4. Drop Jeff's real job photos into `.attic/`, encode them to WebP in `static/images/`, and update `data/gallery.yaml`.
5. Run `scripts/verify-local.sh` and populate `data/evidence.json` for production release approval.
