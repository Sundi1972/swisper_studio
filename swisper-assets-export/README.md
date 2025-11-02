# Swisper Assets Export

This directory contains all frontend assets from the Helvetiq/Swisper project, organized for easy transfer to Swisper Studio.

## Directory Structure

```
swisper-assets-export/
├── logos/                    # Main Swisper logos and branding
│   ├── swisperLogo.svg      # Main Swisper logo (full wordmark + shield)
│   ├── favicon.svg          # Favicon (shield only)
│   └── avatar-1.svg         # User avatar icon
│
├── icons/                    # UI Icons (85 icons total)
│   ├── accessibility.svg
│   ├── add.svg
│   ├── apple.svg
│   ├── bookmark_active.svg
│   ├── bookmark.svg
│   ├── calendar.svg
│   ├── check.svg
│   ├── chevron_down.svg
│   ├── chevron_left.svg
│   ├── chevron_right.svg
│   ├── chevron_up.svg
│   ├── close.svg
│   ├── code.svg
│   ├── control.svg
│   ├── copy.svg
│   ├── delete.svg
│   ├── description.svg
│   ├── digitec.svg
│   ├── discord.svg
│   ├── doc.svg
│   ├── download.svg
│   ├── draft.svg
│   ├── DragIndicatorOutlined.svg
│   ├── edit.svg
│   ├── enter.svg
│   ├── error.svg
│   ├── flame.svg
│   ├── forward.svg
│   ├── full_screen_mode.svg
│   ├── gmail.svg
│   ├── google.svg
│   ├── home.svg
│   ├── incognito.svg
│   ├── info.svg
│   ├── integrations.svg
│   ├── language.svg
│   ├── link_off.svg
│   ├── linkedin.svg
│   ├── location.svg
│   ├── lock.svg
│   ├── logout.svg
│   ├── mail.svg
│   ├── mailchimp.svg
│   ├── mic.svg
│   ├── microsoft.svg
│   ├── more.svg
│   ├── new_chat.svg
│   ├── notifications.svg
│   ├── office365.svg
│   ├── open_in_full.svg
│   ├── open_in_new.svg
│   ├── pdf.svg
│   ├── pin_active.svg
│   ├── pin.svg
│   ├── ppt.svg
│   ├── preferences.svg
│   ├── profile.svg
│   ├── quote.svg
│   ├── remove.svg
│   ├── reply.svg
│   ├── sbb.svg
│   ├── search.svg
│   ├── settings.svg
│   ├── share.svg
│   ├── sidemenu.svg
│   ├── sonos.svg
│   ├── split_view_mode.svg
│   ├── stop.svg
│   ├── success.svg
│   ├── table.svg
│   ├── telegram.svg
│   ├── text_overflow.svg
│   ├── text_wrap.svg
│   ├── the_guardian.svg
│   ├── theme.svg
│   ├── thumbs-down.svg
│   ├── thumbs-up.svg
│   ├── toggle_on.svg
│   ├── visibility_off.svg
│   ├── visibility.svg
│   ├── voice.svg
│   ├── warning.svg
│   ├── whatsapp.svg
│   └── xls.svg
│
├── images/                   # Loading and misc images
│   └── loading-swisper.png  # Loading animation/spinner
│
├── onboarding/              # Onboarding screen images
│   ├── welcome.png
│   ├── tone-preview.png
│   ├── respond-format-preview.png
│   ├── full-name-avatar.png
│   ├── feature-1.png
│   ├── avatar-4.png
│   ├── avatar-3.png
│   ├── avatar-2.png
│   └── avatar-1.png
│
└── marketing/               # Marketing website assets
    ├── logo-marketing.svg
    ├── logo-normal.svg
    ├── logo-only-shield.svg
    └── favicon-marketing.svg

```

## Key Assets

### Primary Branding

#### Main Logo (`logos/swisperLogo.svg`)
- **Full wordmark with shield icon**
- Dimensions: 150x40
- Colors: White text (#FFFFFF) + Cyan blue shield (#00A9DD)
- Use for: App headers, main branding

#### Favicon/Shield (`logos/favicon.svg`)
- **Shield icon only** (no text)
- Dimensions: 36x40
- Color: Cyan blue (#00A9DD)
- Use for: Favicons, small icons, app icons

### Icon Set (85 Icons)

All icons are in SVG format and include:
- **Navigation**: home, sidemenu, chevron (up/down/left/right)
- **Actions**: add, edit, delete, copy, share, download
- **Communication**: mail, reply, forward, notifications
- **Integrations**: google, microsoft, gmail, office365, apple
- **UI Controls**: close, search, settings, theme, preferences
- **Status**: success, error, warning, info
- **Features**: voice, mic, calendar, bookmark, pin
- **File Types**: pdf, doc, ppt, xls
- **Social**: linkedin, whatsapp, telegram, discord

### Onboarding Assets

9 PNG images for user onboarding flow:
- Welcome screen
- Avatar options (4 variants)
- Feature previews
- Settings previews (tone, response format)

### Marketing Assets

4 logo variants for marketing website:
- Full logo
- Logo with normal styling
- Shield-only variant
- Marketing-specific favicon

## Color Palette

Based on the logos:

- **Primary Blue**: `#00A9DD` (Swisper cyan blue)
- **White**: `#FFFFFF`
- **Text/Dark**: Various (used in different contexts)

## File Formats

- **Logos**: SVG (scalable vector graphics)
- **Icons**: SVG (scalable vector graphics)
- **Onboarding Images**: PNG (raster graphics)
- **Loading Images**: PNG (raster graphics)

## Usage Recommendations

### For Swisper Studio

1. **Primary Logo**: Use `logos/swisperLogo.svg` for main branding
2. **Favicon**: Use `logos/favicon.svg` for browser icons
3. **Icons**: Import needed icons from `icons/` directory
4. **Loading States**: Use `images/loading-swisper.png`

### Integration Tips

- All SVG files can be imported directly into React/Vue/Angular components
- Icons can be used as inline SVG or as img src
- Consider creating an icon component library from the icons directory
- PNG images are optimized for web use

## Source Locations (Original Project)

For reference, these assets came from:

- **Logos**: `frontend/src/assets/` and `frontend/public/`
- **Icons**: `packages/icons/src/svg/`
- **Onboarding**: `frontend/public/onboarding/`
- **Images**: `frontend/public/`
- **Marketing**: `marketing/public/img/`

## License

These assets are part of the Swisper project. Please ensure proper licensing when using in Swisper Studio.

---

**Last Updated**: November 2, 2025
**Exported From**: Helvetiq Project (Swisper Frontend)
**Total Assets**: ~100 files

