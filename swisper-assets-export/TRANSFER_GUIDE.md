# Swisper Assets Transfer Guide

## Quick Start

All Swisper frontend assets have been collected and organized in this directory for easy transfer to **Swisper Studio**.

## What's Included

**Total Files**: 102 assets
**Total Size**: 6.5 MB (5.6 MB compressed)

### Asset Breakdown

1. **Logos** (3 files)
   - Main Swisper logo (wordmark + shield)
   - Favicon (shield only)
   - Avatar icon

2. **Icons** (85 files)
   - Complete UI icon set in SVG format
   - Navigation, actions, integrations, status indicators
   - File type icons, social media icons

3. **Images** (1 file)
   - Loading/spinner image

4. **Onboarding** (9 files)
   - Welcome screens
   - Avatar options
   - Feature previews

5. **Marketing** (4 files)
   - Logo variants for marketing website
   - Alternative favicon

## Transfer Options

### Option 1: Use the Compressed Archive (Recommended)

A compressed file is available in the parent directory:

```bash
# Location:
/root/projects/helvetiq/swisper-assets.tar.gz
```

**To extract in Swisper Studio project:**
```bash
tar -xzf swisper-assets.tar.gz
```

This will create the `swisper-assets-export/` directory with all assets organized.

### Option 2: Copy the Directory

```bash
# From current location to Swisper Studio:
cp -r /root/projects/helvetiq/swisper-assets-export /path/to/swisper-studio/assets/
```

### Option 3: Selective Copy

Copy only what you need:

```bash
# Example: Copy only logos and icons
cp -r swisper-assets-export/logos /path/to/swisper-studio/src/assets/
cp -r swisper-assets-export/icons /path/to/swisper-studio/src/assets/
```

## Integration into Swisper Studio

### Recommended Project Structure

```
swisper-studio/
├── src/
│   ├── assets/
│   │   ├── logos/           # From swisper-assets-export/logos/
│   │   ├── icons/           # From swisper-assets-export/icons/
│   │   └── images/          # From swisper-assets-export/images/
│   └── ...
└── public/
    ├── favicon.svg          # From swisper-assets-export/logos/favicon.svg
    └── onboarding/          # From swisper-assets-export/onboarding/
```

### Usage Examples

#### React/TypeScript

```typescript
// Import logo
import SwisperLogo from '@/assets/logos/swisperLogo.svg';

// Use in component
function Header() {
  return (
    <img src={SwisperLogo} alt="Swisper" />
  );
}
```

#### Inline SVG

```typescript
// Import as React component (with appropriate loader)
import { ReactComponent as SearchIcon } from '@/assets/icons/search.svg';

function SearchButton() {
  return <SearchIcon />;
}
```

#### As Image Source

```typescript
// Direct image reference
<img src="/assets/icons/calendar.svg" alt="Calendar" />
```

## Key Assets Reference

### Must-Have Assets

1. **swisperLogo.svg** - Main brand logo
2. **favicon.svg** - Browser favicon
3. **loading-swisper.png** - Loading spinner
4. **icons/** - Complete icon set for UI

### Brand Colors

- **Primary Blue**: `#00A9DD` (Swisper cyan)
- **White**: `#FFFFFF`

### Icon Categories

- **Navigation**: home, sidemenu, chevron variants
- **Actions**: add, edit, delete, copy, share
- **Communication**: mail, notifications, reply
- **Integrations**: google, microsoft, gmail, office365
- **Features**: voice, mic, calendar, bookmark
- **Status**: success, error, warning, info

## Next Steps

1. **Transfer the assets** using one of the methods above
2. **Review the README.md** in this directory for detailed asset descriptions
3. **Update import paths** in Swisper Studio to match new asset locations
4. **Test the integration** to ensure all assets load correctly
5. **Consider creating an icon library** for reusable icon components

## File Formats

- **SVG Files**: Scalable vector graphics (logos, icons)
  - Recommended for: Logos, icons, graphics
  - Benefits: Scalable, small file size, CSS styleable

- **PNG Files**: Raster graphics (onboarding, images)
  - Recommended for: Photos, complex images, loading animations
  - Benefits: Wide compatibility, good for photographs

## Support

For questions about specific assets or integration:

1. Check `README.md` for detailed asset descriptions
2. Review source locations in the README
3. Refer to original Helvetiq project structure

---

**Exported**: November 2, 2025
**Source**: Helvetiq/Swisper Project
**Target**: Swisper Studio

✅ All assets are ready for transfer!

