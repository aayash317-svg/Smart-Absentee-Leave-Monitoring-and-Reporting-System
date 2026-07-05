---
name: Precision Monitor
colors:
  surface: '#faf8ff'
  surface-dim: '#d9d9e5'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3fe'
  surface-container: '#ededf9'
  surface-container-high: '#e7e7f3'
  surface-container-highest: '#e1e2ed'
  on-surface: '#191b23'
  on-surface-variant: '#434655'
  inverse-surface: '#2e3039'
  inverse-on-surface: '#f0f0fb'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#006e2d'
  on-secondary: '#ffffff'
  secondary-container: '#7cf994'
  on-secondary-container: '#007230'
  tertiary: '#943700'
  on-tertiary: '#ffffff'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#7ffc97'
  secondary-fixed-dim: '#62df7d'
  on-secondary-fixed: '#002109'
  on-secondary-fixed-variant: '#005320'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#faf8ff'
  on-background: '#191b23'
  surface-variant: '#e1e2ed'
typography:
  h1:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h1-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
  h2:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.3'
  h3:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: '1.4'
  section-title:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.5'
  body:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  small:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.5'
  label:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style

The design system is built for a Smart Absentee Leave Monitoring and Reporting System. The brand personality is authoritative yet approachable, focusing on clarity, efficiency, and enterprise-grade reliability. The target audience includes HR administrators, department heads, and executives who require immediate, actionable insights into workforce availability.

The design style is **Modern SaaS Minimalist**. It draws inspiration from the utility of Linear and the structured clarity of Microsoft Fluent Design. The interface prioritizes content over chrome, utilizing ample whitespace and a rigorous grid to reduce cognitive load. The emotional response should be one of "controlled transparency"—users should feel that the data is accurate, the system is stable, and the next action is always intuitive.

## Colors

The color palette is rooted in a professional "Enterprise Blue" to signal trust and logic. 

- **Primary Blue (#2563EB)** is used for primary actions, active navigation states, and key data focal points.
- **Functional Colors** (Green, Orange, Red) are reserved strictly for status communication: Green for approved leave, Orange for pending or low-threshold warnings, and Red for unauthorized absences or critical alerts.
- **Neutral Scales** maintain a clean hierarchy. The **Background (#F8FAFC)** provides a cool-toned canvas that allows **Surface (#FFFFFF)** cards to pop with subtle contrast. 
- **Typography** uses a deep Navy-Black for primary text to ensure high legibility and a Slate-Gray for secondary metadata.

## Typography

This design system utilizes **Inter** exclusively to leverage its exceptional legibility in data-heavy environments. 

- **Headlines:** Use tighter letter spacing and heavier weights to anchor pages. 
- **Body Text:** Uses a standard 16px base for comfort. 
- **Labels:** Small, uppercase labels with increased letter spacing should be used for table headers and category tags to differentiate them from interactive data.
- **Scaling:** On mobile devices, H1 scales down to 28px to prevent awkward text wrapping in dashboard headers.

## Layout & Spacing

The system follows a strict **8px linear scale**. All margins, paddings, and component heights must be multiples of 8.

- **Grid:** A 12-column fluid grid is used for desktop (breakpoints at 1440px and 1200px). Tablet uses an 8-column grid, and mobile uses a 4-column fluid grid.
- **Sidebar:** The primary navigation sidebar is fixed at 280px on desktop to ensure consistent information density.
- **Margins:** Page-level containers use a 32px margin on desktop to create a "breathable" frame around data cards. 
- **Alignment:** Internal card padding is standardized at 24px (lg) to ensure high-density data doesn't feel cramped.

## Elevation & Depth

This design system uses a **Tonal Layering** approach combined with **Ambient Shadows** to create hierarchy without clutter.

1.  **Level 0 (Background):** #F8FAFC. The lowest layer.
2.  **Level 1 (Cards/Surface):** #FFFFFF with a 1px solid #E2E8F0 border. No shadow. Used for standard data sections.
3.  **Level 2 (Interactive/Floating):** #FFFFFF with a soft, diffused shadow (0px 4px 12px rgba(15, 23, 42, 0.05)). Used for hovered cards and dropdown menus.
4.  **Level 3 (Modals/Dialogs):** #FFFFFF with a deep, sophisticated shadow (0px 12px 32px rgba(15, 23, 42, 0.1)).

Avoid using heavy black shadows. Shadows should feel like "ambient occlusion" rather than direct light sources.

## Shapes

The shape language is "Soft-Modern." While the system is professional, the generous corner radii prevent it from feeling sterile or cold.

- **Buttons & Inputs:** Standardized at 12px to create a friendly, "squircle-like" interactive feel.
- **Data Cards:** 16px radius creates a clear distinction between the page background and the content containers.
- **Dialogs:** 18px radius provides a distinct, "contained" look for high-priority interruptions.
- **Chips/Status Tags:** Should be fully pill-shaped (radius: 999px) to contrast against the more structured rectangular inputs.

## Components

- **Buttons:** Primary buttons use a solid #2563EB background with White text. Secondary buttons use a #FFFFFF fill with a 1px border (#E2E8F0).
- **Inputs:** Fields use a 12px radius, a 1px #E2E8F0 border, and a subtle #F8FAFC background. On focus, the border transitions to #2563EB with a 2px outer glow.
- **Cards:** Dashboard cards must include a standard 24px internal padding. Titles within cards should use the "Section Title" typography spec.
- **Status Chips:** Use 12px (Small) Semi-bold text. Backgrounds should be 10% opacity of the functional color (e.g., Green #16A34A at 10% opacity) with 100% opacity text for accessibility.
- **Sidebar:** Use the Dark #0F172A background for the sidebar to create high contrast with the main content area, with active states indicated by a #2563EB left-edge accent line.
- **Data Tables:** Row height should be 56px (7 units). Use subtle 1px bottom borders (#E2E8F0). Avoid vertical borders between columns.