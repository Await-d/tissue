# Frontend Development

## Prerequisites

This project uses [pnpm](https://pnpm.io/) as the package manager.

### Install pnpm

```bash
npm install -g pnpm
# or
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

## Development

### Install dependencies

```bash
pnpm install
```

### Start development server

```bash
pnpm run dev
```

### Build for production

```bash
pnpm run build
```

### Preview production build

```bash
pnpm run preview
```

## Why pnpm?

- **Fast**: pnpm is 2x faster than npm
- **Efficient**: Uses a content-addressable store
- **Strict**: Creates a non-flat node_modules by default
- **Reliable**: Has built-in support for monorepos

## Migration from npm

The project has been migrated from npm to pnpm. The main changes:

- Removed `package-lock.json`
- Added `.npmrc` configuration
- Updated Dockerfile to use pnpm
- Updated GitHub Actions to use pnpm

**Note**: After pulling these changes, you need to:

```bash
cd frontend
pnpm install
```

This will generate `pnpm-lock.yaml` which should be committed to version control.
