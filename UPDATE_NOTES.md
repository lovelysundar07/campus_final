# MS College Management System — v3 update notes

This package updates the previously delivered v2 project (it does not use the original user-uploaded ZIP as its base).

## Included changes
- Replaced the web crest asset with the uploaded MS crest, prepared as a transparent circular image, and added a small browser favicon.
- Updated the navbar profile avatar to display the signed-in participant/staff profile picture when available.
- Added optional profile picture uploads during participant and staff registration; pictures can still be changed in My Profile.
- Added an unread-notification count badge to the participant Notifications navigation item.
- Improved circular logo/loading animation shadows and smooth visual effects.
- Redesigned generated certificates in a clean violet/white academic style, removed the college seal and principal signature, and added prominent DEMO CERTIFICATE markings.
- Added an administrator results-publishing action to the marks/reports page. Published score rankings group by symposium sub-event, assign prize labels by rank, and notify registered participants.
- Added Leaderboards links for admin, staff, and participant accounts.
- Added `database/migrations/003_leaderboard_results.sql`.

## Database migration order for an existing database
1. Back up the database.
2. Apply `database/migrations/001_project_upgrade.sql` once.
3. Apply `database/migrations/002_profile_images_and_custom_event_types.sql` once.
4. Apply `database/migrations/003_leaderboard_results.sql` once.

Do not re-run a migration that already succeeded. If MySQL reports a duplicate column/table, stop and inspect the schema rather than repeating it.

## Results workflow
1. Assigned staff submit scores from the event detail page.
2. Admin opens Reports / Marks & Results and reviews the marks.
3. Admin selects an event and publishes the results.
4. Registered participants receive notifications; all signed-in roles can access Leaderboards.

Prize labels are assigned by score ranking (first, second, third, then participant). The application cannot guarantee tie-breaking policy beyond the current score/name sort, so the college should review rankings before publishing.

## Validation performed
- Python files passed `compileall` syntax checks.
- Jinja templates parsed without syntax errors.
- Full Flask runtime/DB integration testing could not be performed in this environment because the runtime dependencies and local MySQL/Gemini credentials are not available here.

## v4 refinements (2026-10-29)
- Navbar branding now yields space to navigation links; logged-in dashboards rely on their sidebar branding, while the public home page displays the college logo in the hero badge instead of duplicating it in the navbar.
- Added a consistent back button to authenticated pages.
- Improved light-mode contrast for the home hero.
- Certificate generation now embeds the college crest and lists coordinating staff for the event.
- Admin Staff Requests now lists approved staff and supports pausing/reactivating accounts or removing them from current assignments while retaining historical records.
- Staff listing now receives `approved_staff` from the route so the template renders reliably.
