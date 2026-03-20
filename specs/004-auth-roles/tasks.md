# Tasks: Authentification et gestion des rôles

**Input**: Design documents from `/specs/004-auth-roles/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and configuration for auth feature

- [X] T001 Add auth dependencies (python-jose[cryptography], passlib[bcrypt], python-multipart, email-validator) to apps/backend/pyproject.toml and install in .venv
- [X] T002 [P] Add @nuxtjs/color-mode module to apps/frontend/ and configure in apps/frontend/nuxt.config.ts
- [X] T003 [P] Add JWT/auth environment variables (JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, FIRST_ADMIN_EMAIL, FIRST_ADMIN_PASSWORD) to .env.example and extend Settings class in apps/backend/app/core/config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, security utilities, and shared infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create SQLAlchemy Base model with UUID primary key and created_at mixin in apps/backend/app/models/base.py
- [X] T005 Create User model with UserRole enum (admin/editor), email, hashed_password, is_active, failed_login_attempts, locked_until fields in apps/backend/app/models/user.py
- [X] T006 Generate Alembic migration for users table (upgrade: CREATE TABLE + unique index on email, downgrade: DROP TABLE) in apps/backend/alembic/versions/
- [X] T007 [P] Implement security module with password hash/verify (passlib CryptContext bcrypt), JWT create_access_token, create_refresh_token, decode_token functions in apps/backend/app/core/security.py
- [X] T008 [P] Create Pydantic schemas: LoginRequest, RegisterRequest, TokenResponse, UserResponse in apps/backend/app/schemas/auth.py
- [X] T009 [P] Create useApi composable as single entry point for all API calls (base fetch with auth header injection, error handling) in apps/frontend/app/composables/useApi.ts
- [X] T010 [P] Create shared TypeScript types (UserRole, UserProfile, TokenResponse, LoginPayload, RegisterPayload) in packages/shared/types/auth.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Connexion administrateur (Priority: P1) MVP

**Goal**: Un admin peut se connecter avec email/mot de passe et accéder à l'espace admin. Inclut le verrouillage brute force après 5 échecs.

**Independent Test**: Se connecter avec un compte admin valide, vérifier la redirection vers /admin. Tester des identifiants incorrects, vérifier le message d'erreur générique. Tester le verrouillage après 5 échecs.

### Implementation for User Story 1

- [X] T011 [US1] Implement auth service with authenticate_user method (verify password, check is_active, check locked_until, increment/reset failed_login_attempts, generate tokens, set refresh cookie) in apps/backend/app/services/auth.py
- [X] T012 [US1] Create auth router with POST /api/auth/login endpoint (accept LoginRequest, return TokenResponse, set refresh_token httpOnly cookie) in apps/backend/app/routers/auth.py
- [X] T013 [US1] Register auth router in apps/backend/app/main.py with prefix /api/auth
- [X] T014 [P] [US1] Create login page with email/password form, error display, and redirect to /admin on success in apps/frontend/app/pages/admin/login.vue
- [X] T015 [P] [US1] Create useAuth composable with reactive user state, login method (call /api/auth/login, store access_token in memory, fetch /api/auth/me), logout method (clear state, redirect to login) in apps/frontend/app/composables/useAuth.ts

**Checkpoint**: Admin can log in via the login page and receive tokens. Brute force protection active.

---

## Phase 4: User Story 2 - Protection des routes admin (Priority: P1)

**Goal**: Tout accès non authentifié aux pages /admin/* est redirigé vers /admin/login. L'endpoint /me permet de vérifier l'identité.

**Independent Test**: Accéder à /admin sans token → redirigé vers /admin/login. Accéder avec token valide → page affichée.

### Implementation for User Story 2

- [X] T016 [US2] Implement get_current_user FastAPI dependency (decode JWT from Authorization header, fetch user from DB, check is_active) in apps/backend/app/core/security.py
- [X] T017 [US2] Add GET /api/auth/me endpoint (protected by get_current_user, return UserResponse) in apps/backend/app/routers/auth.py
- [X] T018 [US2] Create Nuxt route middleware that checks auth state on navigation to /admin/* routes, redirects to /admin/login if not authenticated, calls /api/auth/me to validate token on page refresh in apps/frontend/app/middleware/auth.ts
- [X] T019 [P] [US2] Create placeholder admin dashboard page with definePageMeta({ middleware: 'auth' }) in apps/frontend/app/pages/admin/index.vue

**Checkpoint**: Unauthenticated access to /admin/* redirects to login. Authenticated users see the admin page.

---

## Phase 5: User Story 3 - Initialisation premier administrateur (Priority: P1)

**Goal**: Un script crée le premier admin à partir des variables d'environnement. Idempotent.

**Independent Test**: Exécuter le script sur une DB vide → admin créé. Relancer → pas de doublon. Se connecter avec les identifiants du seed.

### Implementation for User Story 3

- [X] T020 [US3] Create seed_admin script that reads FIRST_ADMIN_EMAIL/FIRST_ADMIN_PASSWORD from env, creates admin user if not exists (check by email), uses async session and password hashing in apps/backend/scripts/seed_admin.py (with __main__ entry point)

**Checkpoint**: Platform is bootable - seed admin, log in, access admin space.

---

## Phase 6: User Story 4 - Création de comptes par un administrateur (Priority: P2)

**Goal**: Un admin connecté peut créer de nouveaux comptes (email, password, rôle). Les éditeurs ne peuvent pas créer de comptes. Doublon email refusé.

**Independent Test**: Se connecter en admin, créer un compte éditeur via l'API, vérifier que le nouveau compte peut se connecter.

### Implementation for User Story 4

- [X] T021 [US4] Implement require_role FastAPI dependency (accepts role parameter, checks current_user.role, raises 403 if insufficient) in apps/backend/app/core/security.py
- [X] T022 [US4] Add register_user method to auth service (validate email uniqueness, hash password, create user, return UserResponse) in apps/backend/app/services/auth.py
- [X] T023 [US4] Add POST /api/auth/register endpoint (protected by require_role("admin"), accept RegisterRequest, return 201 UserResponse or 400 on duplicate) in apps/backend/app/routers/auth.py

**Checkpoint**: Admin can create new user accounts. Role-based access control works.

---

## Phase 7: User Story 5 - Navigation admin avec identité et thème (Priority: P2)

**Goal**: Layout admin avec sidebar, header (email utilisateur + bouton déconnexion), et sélecteur dark/light mode persisté localement.

**Independent Test**: Se connecter → sidebar et header visibles, email affiché. Basculer dark/light mode → thème change instantanément et persiste au rechargement.

### Implementation for User Story 5

- [X] T024 [US5] Create admin layout with sidebar navigation, header displaying user email from useAuth state, logout button calling useAuth.logout(), and theme toggle using useColorMode() in apps/frontend/app/layouts/admin.vue
- [X] T025 [US5] Apply admin layout to admin pages: set definePageMeta({ layout: 'admin' }) in apps/frontend/app/pages/admin/index.vue, ensure login page does NOT use admin layout
- [X] T026 [US5] Style admin layout with Tailwind CSS: responsive sidebar, dark mode classes (dark:bg-gray-900, dark:text-white etc.), smooth theme transition in apps/frontend/app/layouts/admin.vue

**Checkpoint**: Admin space has a polished layout with sidebar, user identity, logout, and dark/light mode.

---

## Phase 8: User Story 6 - Maintien de session et renouvellement automatique (Priority: P3)

**Goal**: La session courte (access token 30min) est renouvelée automatiquement via le refresh token (cookie 7 jours) sans interruption pour l'utilisateur.

**Independent Test**: Se connecter, attendre l'expiration de l'access token (ou le simuler), effectuer une action → session renouvelée sans déconnexion. Après expiration du refresh token → redirigé vers login.

### Implementation for User Story 6

- [X] T027 [US6] Add refresh_access_token method to auth service (read refresh cookie, decode token, verify user still active, generate new access token + rotate refresh cookie) in apps/backend/app/services/auth.py
- [X] T028 [US6] Add POST /api/auth/refresh endpoint (read refresh_token from cookie, return new TokenResponse + new refresh cookie, or 401) in apps/backend/app/routers/auth.py
- [X] T029 [US6] Add auto-refresh logic to useAuth: on 401 response, call /api/auth/refresh, retry original request with new token, redirect to login if refresh fails in apps/frontend/app/composables/useAuth.ts
- [X] T030 [US6] Add 401 interceptor in useApi composable that triggers useAuth refresh flow before failing in apps/frontend/app/composables/useApi.ts

**Checkpoint**: Sessions remain active seamlessly for 7 days with automatic token rotation.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Tests, validation, cleanup

- [X] T031 [P] Create pytest fixtures (async client, test DB session, test user factory, auth headers helper) in apps/backend/tests/conftest.py
- [X] T032 [P] Write auth endpoint tests covering: login success, login wrong password, login inactive account, login brute force lockout, register as admin, register as editor (403), register duplicate email, me endpoint, refresh token flow in apps/backend/tests/test_auth.py
- [X] T033 Update .env.example with complete list of all environment variables including auth section
- [X] T034 Run quickstart.md validation: full flow from migration → seed → login → admin access → dark mode toggle

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 Connexion (Phase 3)**: Depends on Foundational
- **US2 Protection routes (Phase 4)**: Depends on US1 (needs login to test protection)
- **US3 Seed admin (Phase 5)**: Depends on Foundational only (can parallel with US1)
- **US4 Création comptes (Phase 6)**: Depends on US2 (needs get_current_user + require_role)
- **US5 Layout admin (Phase 7)**: Depends on US2 (needs auth middleware + useAuth state)
- **US6 Refresh session (Phase 8)**: Depends on US1 (needs login flow to extend)
- **Polish (Phase 9)**: Depends on all user stories

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational)
                        │
                        ├── US3 (Seed admin) ──────────────────┐
                        │                                       │
                        ├── US1 (Connexion) ─── US2 (Routes) ──┼── US4 (Register)
                        │                           │           │
                        │                           ├── US5 (Layout + thème)
                        │                           │
                        └── US6 (Refresh) ──────────┘
                                                    │
                                                    └── Phase 9 (Polish)
```

### Within Each User Story

- Backend tasks before frontend tasks (APIs must exist)
- Service layer before router layer
- Core implementation before integration

### Parallel Opportunities

**Phase 1**: T001 || T002 || T003
**Phase 2**: T004 → T005 → T006 (sequential), T007 || T008 || T009 || T010 (parallel with T004-T006)
**Phase 3**: Backend (T011→T012→T013) || Frontend (T014, T015)
**Phase 4**: T016 → T017, T018 || T019
**Phase 5**: T020 (single task)
**Phase 6**: T021 → T022 → T023
**Phase 7**: T024 → T025 → T026
**Phase 8**: Backend (T027→T028) || Frontend (T029, T030)
**Phase 9**: T031 || T032

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Sequential chain (model depends on base):
Task T004: Create Base model in apps/backend/app/models/base.py
Task T005: Create User model in apps/backend/app/models/user.py
Task T006: Generate Alembic migration

# Parallel with above (independent files):
Task T007: Security module in apps/backend/app/core/security.py
Task T008: Pydantic schemas in apps/backend/app/schemas/auth.py
Task T009: useApi composable in apps/frontend/app/composables/useApi.ts
Task T010: Shared types in packages/shared/types/auth.ts
```

## Parallel Example: Phase 3 (US1 - Connexion)

```bash
# Backend chain (service → router → register):
Task T011: Auth service in apps/backend/app/services/auth.py
Task T012: Auth router in apps/backend/app/routers/auth.py
Task T013: Register router in apps/backend/app/main.py

# Frontend (parallel with backend):
Task T014: Login page in apps/frontend/app/pages/admin/login.vue
Task T015: useAuth composable in apps/frontend/app/composables/useAuth.ts
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 5: US3 (Seed admin - needed to test login)
4. Complete Phase 3: US1 (Connexion)
5. Complete Phase 4: US2 (Protection routes)
6. **STOP and VALIDATE**: Seed admin → login → access admin → logout → redirect to login
7. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational + US3 + US1 + US2 → **MVP fonctionnel** (login/logout/protection)
2. Add US4 (Création comptes) → Admin peut inviter des utilisateurs
3. Add US5 (Layout + thème) → Interface admin complète avec dark/light mode
4. Add US6 (Refresh session) → Sessions fluides sans déconnexions intempestives
5. Polish → Tests, validation, cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Auth is a critical path per constitution → tests in Phase 9 are mandatory
- Refresh token stored in httpOnly cookie (R4 research decision) → frontend never accesses it directly
