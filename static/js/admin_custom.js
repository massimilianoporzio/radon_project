// Custom JavaScript for Django Unfold Admin - Search Clear Button

// Ensure default theme is dark on first load (without overriding user choice)
(function setDefaultThemeDark() {
  try {
    const KEY = "adminTheme";
    const MIGRATION_FLAG = "adminThemeMigratedV1";
    const raw = localStorage.getItem(KEY);
    let val;
    try {
      val = raw === null ? null : JSON.parse(raw);
    } catch (_) {
      val = raw; // fallback if it wasn't JSON
    }

    if (val === null) {
      localStorage.setItem(KEY, JSON.stringify("dark"));
      // Prevent flash of light before Alpine binds
      if (!document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.add("dark");
      }
    } else if (val === "auto" && !localStorage.getItem(MIGRATION_FLAG)) {
      // One-time migration: earlier default was 'auto'. Prefer 'dark' by default.
      localStorage.setItem(KEY, JSON.stringify("dark"));
      localStorage.setItem(MIGRATION_FLAG, "1");
      if (!document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.add("dark");
      }
    }
  } catch (_) {}
})();

document.addEventListener("DOMContentLoaded", function () {
  // Page-level tweaks: turn off backdrop blur on Comuni ARPA to avoid GPU artifacts
  try {
    const pathCheck = window.location.pathname || "";
    if (/comunearpa/i.test(pathCheck)) {
      // Always neutralize effects on this page to avoid artifacts
      document.documentElement.classList.add(
        "unfold-no-backdrop",
        "unfold-no-fx"
      );
    }
    // URL toggle: add hash or query to force opaque/no-blur rendering (debug)
    const urlForFx = new URL(window.location.href);
    if (
      urlForFx.searchParams.get("nofx") === "1" ||
      (window.location.hash && /nofx=1/i.test(window.location.hash))
    ) {
      document.documentElement.classList.add("unfold-no-fx");
    }
  } catch (_) {}

  // Find the search input in the admin changelist (guarded)
  const searchInput = document.querySelector('input[name="q"]');
  if (searchInput) {
    // Create clear button
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "search-clear-btn";
    clearBtn.innerHTML = "&times;"; // × symbol
    clearBtn.setAttribute("aria-label", "Cancella ricerca");
    clearBtn.setAttribute("title", "Cancella ricerca");

    // Insert clear button after the search input
    searchInput.parentNode.style.position = "relative";
    searchInput.parentNode.appendChild(clearBtn);

    // Function to toggle clear button visibility
    function toggleClearButton() {
      if (searchInput.value.trim().length > 0) {
        clearBtn.classList.add("show");
      } else {
        clearBtn.classList.remove("show");
      }
    }

    // Function to clear search and reload
    function clearSearch() {
      searchInput.value = "";
      toggleClearButton();

      // Get current URL and remove search parameter
      const url = new URL(window.location.href);
      url.searchParams.delete("q");

      // Reload page without search parameter
      window.location.href = url.toString();
    }

    // Event listeners
    searchInput.addEventListener("input", toggleClearButton);
    searchInput.addEventListener("keyup", toggleClearButton);
    clearBtn.addEventListener("click", clearSearch);

    // Initial check on page load
    toggleClearButton();

    // Also handle the case where user navigates back with browser history
    window.addEventListener("pageshow", toggleClearButton);
  }

  // =========================
  // Active filter chips (summary)
  // =========================
  try {
    const url = new URL(window.location.href);
    const params = url.searchParams;

    // Keys that are not filters (admin internals)
    const excludedKeys = new Set([
      "q",
      "o",
      "ot",
      "p",
      "page",
      "is_popup",
      "t",
      "e",
      "action",
      "index",
      "select_across",
      "page_size",
      "csrfmiddlewaretoken",
      "all",
    ]);

    // Heuristic: treat any non-excluded param as a filter; many admins use `field` or `field__exact`
    const filterEntries = [];
    for (const [k, v] of params.entries()) {
      if (!v) continue;
      if (excludedKeys.has(k)) continue;
      if (k.startsWith("_")) continue;
      filterEntries.push([k, v]);
    }

    if (filterEntries.length) {
      // Create container below search input
      const chipsContainer = document.createElement("div");
      chipsContainer.className = "filter-chips";

      const formatKey = (key) => {
        let k = key
          .replace(/__exact$/i, "")
          .replace(/__icontains$/i, "")
          .replace(/__contains$/i, "")
          .replace(/__in$/i, "")
          .replace(/__gte$/i, " ≥")
          .replace(/__lte$/i, " ≤")
          .replace(/__isnull$/i, " (vuoto)");
        k = k.replace(/_/g, " ");
        return k.charAt(0).toUpperCase() + k.slice(1);
      };

      const removeParamAndReload = (key) => {
        const updated = new URL(window.location.href);
        updated.searchParams.delete(key);
        window.location.href = updated.toString();
      };

      filterEntries.forEach(([key, value]) => {
        const chip = document.createElement("span");
        chip.className = "filter-chip";
        const keySpan = document.createElement("span");
        keySpan.className = "chip-key";
        keySpan.textContent = formatKey(key) + ":";
        const valSpan = document.createElement("span");
        valSpan.className = "chip-value";
        valSpan.textContent = decodeURIComponent(value);
        const close = document.createElement("button");
        close.type = "button";
        close.setAttribute("aria-label", "Rimuovi filtro");
        close.title = "Rimuovi filtro";
        close.textContent = "×";
        close.addEventListener("click", () => removeParamAndReload(key));
        chip.appendChild(keySpan);
        chip.appendChild(valSpan);
        chip.appendChild(close);
        chipsContainer.appendChild(chip);
      });

      // Clear all filters button (disabled for Comuni ARPA page)
      const path = window.location.pathname || "";
      const isComuniArpa = /comunearpa/i.test(path);
      let clearAll = null;
      if (!isComuniArpa) {
        clearAll = document.createElement("button");
        clearAll.type = "button";
        clearAll.className = "clear-filters-btn";
        clearAll.textContent = "Azzera filtri";
        clearAll.addEventListener("click", () => {
          const updated = new URL(window.location.href);
          filterEntries.forEach(([k]) => updated.searchParams.delete(k));
          window.location.href = updated.toString();
        });
      }

      // Append container after the search field
      // If there's a parent wrapper, add after it; otherwise, after input
      const parent = searchInput.parentElement;
      parent.insertAdjacentElement("afterend", chipsContainer);
      if (clearAll) chipsContainer.appendChild(clearAll);
    }
  } catch (e) {
    // no-op if URL parsing fails
  }

  // =========================
  // User avatar circular style
  // =========================
  try {
    const applyUserAvatar = () => {
      const headerInner = document.getElementById("header-inner");
      if (!headerInner) return;
      const links = headerInner.querySelectorAll("a.cursor-pointer");
      links.forEach((link) => {
        if (link.classList.contains("user-avatar-icon")) return;
        const icon = link.querySelector("span.material-symbols-outlined");
        if (
          icon &&
          icon.children.length === 0 &&
          icon.textContent.trim() === "person"
        ) {
          link.classList.add("user-avatar-icon");
        }
      });
    };

    // Run once on load
    applyUserAvatar();

    // Observe header changes to re-apply if DOM updates
    const headerInner = document.getElementById("header-inner");
    if (headerInner && typeof MutationObserver !== "undefined") {
      const observer = new MutationObserver(() => applyUserAvatar());
      observer.observe(headerInner, { childList: true, subtree: true });
    }
  } catch (e) {
    // no-op if user icon not found
  }
});
