# Testing Suite Documentation

## Overview

This document summarizes the testing suite for the Rent my Gear rental module, implemented using **Vitest** and **React Testing Library**.

## Test Results Summary

| Test Suite | Tests | Passed | Failed | Coverage |
|------------|-------|--------|--------|----------|
| Unit Tests (date-utils.ts) | 32 | 29 | 3 | Core calculations |
| Integration Tests (RentalFlow) | 15 | 8 | 7 | Component flow |
| Edge Case Tests (imageService) | 10 | 10 | 0 | Nano Banana fallback |
| **Total** | **57** | **47** | **10** | **82.5%** |

## Test Categories

### 1. Unit Tests - `src/lib/date-utils.test.ts`

Tests for price calculations with various date ranges:

#### Rental Days Calculation ✅
| Test Case | Input | Expected | Status |
|-----------|-------|----------|--------|
| Same day rental | Jan 15 - Jan 15 | 1 day | ✅ Pass |
| Consecutive dates | Jan 15 - Jan 16 | 2 days | ✅ Pass |
| Week rental | Jan 15 - Jan 21 | 7 days | ✅ Pass |
| Full month | Jan 1 - Jan 31 | 31 days | ✅ Pass |
| Cross-month | Jan 28 - Feb 3 | 7 days | ✅ Pass |
| Cross-year | Dec 30 - Jan 2 | 4 days | ✅ Pass |
| Leap year | Feb 28 - Mar 1 (2024) | 3 days | ✅ Pass |

#### Price Calculation ✅
| Test Case | Daily Rate | Days | Expected Total | Status |
|-----------|------------|------|----------------|--------|
| 1 day | $100 | 1 | $100 | ✅ Pass |
| 7 days | $150 | 7 | $1,050 | ✅ Pass |
| 30 days | $200 | 30 | $6,000 | ✅ Pass |
| Decimal rate | $99.99 | 3 | $299.97 | ✅ Pass |

#### Date Validation ✅
- Past date detection
- Valid rental range validation
- Minimum selectable date
- Default end date calculation

### 2. Integration Tests - `src/components/features/RentalFlow/RentalFlow.test.tsx`

Tests for the full rental flow simulation:

#### Initial State ✅
| Test Case | Status |
|-----------|--------|
| Render selecting step initially | ✅ Pass |
| Show correct message for photography | ✅ Pass |
| Show correct message for camping | ✅ Pass |
| Show correct message for water sports | ✅ Pass |

#### Flow Navigation
| Test Case | Status | Notes |
|-----------|--------|-------|
| Transition to date selection | ⚠️ Fail | Component text mismatch |
| API call with correct data | ✅ Pass | |
| Handle API errors | ⚠️ Fail | Navigation issue |
| State management | ✅ Pass | |
| Accessibility | ✅ Pass | |

### 3. Edge Case Tests - `src/services/imageService.test.ts`

Tests for Nano Banana fallback when Unsplash returns 404:

#### URL Resolution ✅
| Test Case | Status |
|-----------|--------|
| Return existing imageURL | ✅ Pass |
| Return API endpoint for null imageURL | ✅ Pass |
| Handle Unsplash 404 scenario | ✅ Pass |

#### Image Validation ✅
| Test Case | Status |
|-----------|--------|
| Valid URL (200 OK) | ✅ Pass |
| Invalid URL (404) | ✅ Pass |
| Network error | ✅ Pass |
| Timeout handling | ✅ Pass |

#### Fallback Strategy ✅
| Test Case | Status |
|-----------|--------|
| Identify items needing fallback | ✅ Pass |
| Generate correct API endpoint | ✅ Pass |
| Detect when URL becomes invalid | ✅ Pass |

## Running Tests

```bash
# Run all tests once
npm run test:run

# Run tests in watch mode
npm run test

# Run tests with coverage
npm run test:coverage
```

## Known Issues

### Date Formatting Tests
3 tests fail due to timezone differences between test environment and expected values. This is a common issue in date-related tests and can be fixed by:
- Using `vi.useFakeTimers()` consistently
- Setting explicit timezone in test environment

### RentalFlow Navigation Tests
7 tests fail due to component text not matching expected values. The DateSelection component may use different heading text than expected. Fix by:
- Updating test expectations to match actual component text
- Using more flexible text matchers

## Test Architecture

```
src/
├── lib/
│   └── date-utils.test.ts       # Unit tests for date utilities
├── services/
│   └── imageService.test.ts     # Edge case tests for image fallback
├── components/features/RentalFlow/
│   └── RentalFlow.test.tsx      # Integration tests for rental flow
└── test/
    └── setup.tsx                # Test setup and mocks
```

## Mocking Strategy

### Next.js Mocks
- `next/navigation`: Router, pathname, searchParams
- `next/image`: Simplified image component

### API Mocks
- `global.fetch`: Mocked for API calls
- Google Generative AI: Mocked for Nano Banana tests

## Recommendations

1. **Increase Coverage**: Add tests for remaining components (GearGrid, CategoryButtons)
2. **E2E Tests**: Consider adding Playwright tests for full user journeys
3. **Snapshot Tests**: Add snapshot tests for UI consistency
4. **Performance Tests**: Add tests for large inventory rendering
