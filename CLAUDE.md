# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 명령어

```bash
npm run dev        # Turbopack 개발 서버
npm run build      # Turbopack 프로덕션 빌드
npm run start      # 프로덕션 서버 실행
npm run lint       # ESLint 실행
```

테스트 프레임워크는 설정되어 있지 않음.

## 기술 스택

- **Next.js 15** (App Router, Turbopack)
- **React 19**
- **TypeScript 5** (strict mode, path alias `@/*` → `./src/*`)
- **TailwindCSS v4** — `tailwind.config.js` 없음, CSS-first 방식 (`src/app/globals.css`에서 설정)
- **shadcn/ui** (`base-nova` 스타일) + **@base-ui/react** (headless primitives)
- **next-themes** — 다크모드

## 아키텍처

### 컴포넌트 레이어

1. `src/components/ui/` — shadcn/ui 기반 컴포넌트 (직접 소유, copy-paste 방식)
2. `@base-ui/react` — headless primitive (shadcn/ui 내부에서 사용)
3. `class-variance-authority (CVA)` — 컴포넌트 변형(variant) 정의
4. `cn()` (`src/lib/utils.ts`) — `clsx` + `tailwind-merge` 조합 유틸리티

### 스타일링

TailwindCSS v4는 CSS-first 방식이므로 JS config 파일 대신 `globals.css`에서 테마 설정:
```css
@import "tailwindcss";
/* CSS custom properties로 color token 정의 */
```
다크모드는 `data-[mode=dark]:` 또는 `.dark:` 변형으로 처리.

### Base UI 사용 패턴

`@base-ui/react` 컴포넌트는 `render` prop으로 커스텀 엘리먼트 주입:
```tsx
<Tooltip.Root>
  <Tooltip.Trigger render={<button />}>호버</Tooltip.Trigger>
  <Tooltip.Popup>내용</Tooltip.Popup>
</Tooltip.Root>
```

### 레이아웃 구조

- `src/app/layout.tsx` — Server Component, `ThemeProvider`(next-themes)와 `TooltipProvider` 전체 래핑
- `<html suppressHydrationWarning>` — next-themes hydration 불일치 방지 필수
- 모든 인터랙티브 UI 컴포넌트는 `"use client"` 선언

### 경로 별칭

`@/` → `src/` (예: `import { cn } from "@/lib/utils"`)
