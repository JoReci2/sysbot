# GitHub Workflows

This directory contains GitHub Actions workflows for the SysBot project.

## Workflows

### Release Workflow (`release.yml`)

**Trigger**: Automatically runs when a tag matching the pattern `*.*.*` is pushed (e.g., `1.0.0`, `2.1.3`).

**Features**:
- Builds Python package (wheel and source distribution)
- Extracts issues from milestone matching the tag version
- Generates Software Bill of Materials (SBOM) using CycloneDX
- Runs vulnerability analysis with Safety
- Builds PDF documentation from Antora documentation
- Creates a GitHub release with:
  - Release notes from milestone issues
  - Python package artifacts
  - SBOM report
  - Vulnerability analysis report
  - PDF documentation

**Usage**:
1. Create a milestone matching the version (e.g., "1.0" for tag "1.0.0")
2. Add issues to the milestone
3. Close the issues when complete
4. Create and push a tag:
   ```bash
   git tag 1.0.0
   git push origin 1.0.0
   ```

### Documentation Workflow (`docs.yml`)

**Trigger**: 
- Automatically runs when changes are pushed to the `main` branch in:
  - `docs/**` directory
  - `antora-playbook.yml` file
  - The workflow file itself
- Can also be triggered manually via workflow dispatch

**Features**:
- Builds Antora documentation from `/docs` directory
- Deploys to GitHub Pages
- Generates static HTML site

**First-Time Setup**:
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. The workflow will automatically deploy documentation

**URL**: After deployment, documentation will be available at `https://joreci2.github.io/sysbot`

## Requirements

### For Release Workflow
- Repository must have issues and milestones enabled
- GitHub Pages must be enabled (for including documentation URL in releases)
- Python 3.11+ (configured in workflow)

### For Documentation Workflow
- GitHub Pages must be enabled in repository settings
- Antora documentation must be in `/docs` directory
- Valid `antora-playbook.yml` in repository root

## Permissions

Both workflows use the following permissions:
- `contents: write` - For creating releases and pushing artifacts
- `packages: write` - For publishing packages
- `pages: write` - For deploying to GitHub Pages
- `id-token: write` - For GitHub Pages deployment

## Development

To test workflows locally:

1. **Validate YAML syntax**:
   ```bash
   yamllint .github/workflows/
   ```

2. **Test package build**:
   ```bash
   python -m build
   ```

3. **Test documentation build**:
   ```bash
   antora antora-playbook.yml
   ```

## Troubleshooting

### Release workflow fails on PDF generation
- The workflow includes fallback mechanisms for PDF generation
- If Antora PDF fails, it attempts direct asciidoctor-pdf conversion
- A placeholder file is created if all PDF generation methods fail

### Documentation workflow fails to deploy
- Verify GitHub Pages is enabled in repository settings
- Check that the Pages source is set to "GitHub Actions"
- Review workflow logs for specific errors

### Milestone issues not appearing in release notes
- Ensure milestone title matches the major.minor version (e.g., "1.0" for tag "1.0.0")
- Verify issues are closed and assigned to the milestone
- Check workflow logs for milestone detection
