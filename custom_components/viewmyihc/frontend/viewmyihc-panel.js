/* ViewMyIHC panel – vanilla web component, styled with Home Assistant CSS variables. */

const I18N = {
  da: {
    title: "ViewMyIHC", project: "Projekt", admin: "Administration", refresh: "Opdater",
    all: "Alle", installation: "Installation", programs: "Programmer",
    search: "Søg på navn eller ID …", loading: "Indlæser projekt fra controlleren …",
    copied: "Kopieret", copy: "Kopiér ID", noResults: "Ingen resultater", id: "ID", hex: "Hex",
    path: "Placering", note: "Note", values: "Egenskaber", links: "Forbindelser", current: "Aktuel værdi",
    noSelection: "Vælg et element i træet", close: "Luk",
    noIhcTitle: "IHC-integrationen er ikke sat op",
    noIhcText: "ViewMyIHC bruger forbindelsen fra Home Assistants indbyggede IHC-integration. Sæt den op i configuration.yaml (ihc:) og genstart, så dukker projektet op her.",
    errorTitle: "Kunne ikke hente fra controlleren", retry: "Prøv igen",
    entitiesTitle: "Entiteter i ihc-integrationen", inYaml: "i din YAML ({file}:{line})",
    entitiesLead: "Alle entiteter, som ihc-integrationen har oprettet (fra din YAML eller auto-opsætning), plus poster i din YAML, der venter på en genstart. Hold øje med tilstanden direkte her.",
    entSearch: "Søg på navn, entitet eller id …", allTypes: "Alle", showInTree: "Vis i træet", entNone: "Ingen entiteter fundet.",
    noList: "Ingen liste endnu", entryCount: "{n} poster",
    createYamlLead: "ViewMyIHC opretter ikke entiteten selv. Du får den YAML-post, som skal indsættes i din egen ihc-opsætning, og vi kontrollerer, om den findes allerede.",
    nameHelp: "Valgfrit. Udelades navnet, bruger ihc navnet ihc_{id}.", optionsFor: "Indstillinger for {platform}",
    livePreview: "YAML-post", makeYaml: "Opret YAML", yourEntry: "Din YAML-post", copyYaml: "Kopiér YAML", back: "Tilbage",
    step1: "Kopiér posten.", step2: "Indsæt den i din ihc-opsætning på det sted, der er vist.", stepRestart: "Genstart Home Assistant (ihc læser sin opsætning ved opstart).",
    verifyBtn: "Tjek om den er indsat", verifyFoundYaml: "Fundet i din YAML ({file}:{line}) – genstart Home Assistant, så oprettes entiteten.",
    verifyFoundEntity: "Findes i ihc: {entity}.", verifyNone: "Ikke fundet endnu – indsæt posten og tjek igen.",
    whereAppend: "Indsæt i {file} direkte efter linje {line}", whereKey: " (under {platform}: i {kfile}:{kline}).",
    whereAddKey: "Indsæt i {file} direkte efter linje {line}. Det opretter nøglen {platform}: under din controller.",
    whereNewFile: "Opret en ny .yaml-fil i mappen {dir} med dette indhold (mappen indlæses med !include_dir_merge_list).",
    whereManual: "Jeg kunne ikke følge din opsætning automatisk. Sæt posten som et element under {platform}: under din controller i ihc-opsætningen.",
    existsTitle: "Findes allerede i ihc-integrationen", existsYaml: "står i din YAML ({file}:{line}), afventer genstart", disabledTag: "deaktiveret",
    madeHere: "oprettet i ViewMyIHC", openEntity: "Åbn entiteten", takenBadge: "Findes", haChipTitle: "Findes i ihc: {list}",
    existsBlocked: "Der findes allerede en {platform}-entitet for denne ressource ({entity}). Home Assistant ville afvise en dublet.",
    existsBlockedAll: "Der findes allerede: {list}. Typer, der allerede findes, kan ikke oprettes igen (Home Assistant afviser dubletter), men du kan vælge en anden type.",
    existsOther: "Der findes allerede en entitet af en anden type: {list}. Du kan godt oprette en ekstra, men tjek at det er meningen.",
    checkTitle: "Kontrol af opsætning", checkAgain: "Kontrollér igen", checking: "Kontrollerer …",
    checkReadOnly: "Kun læsning – ViewMyIHC ændrer aldrig dine filer og læser ikke secrets.yaml.",
    scannedFiles: "{n} filer gennemgået", wiredOk: "Koblet på – genstart Home Assistant, så dukker entiteten op",
    seeEntitiesTab: "Se fanen Entiteter for detaljer.",
    foundIn: "Din ihc-opsætning er defineret i {file} linje {line}.", controllerIn: "Controlleren står i {file} linje {line}.",
    insertTitle: "Indsæt disse linjer", insertTitleLater: "Gør klar til senere (først nødvendigt, når du opretter entiteter)", insertHere: "I {file} direkte efter linje {line} (indrykning: {indent} mellemrum):",
    mergeTitle: "Flet {platform} manuelt", mergeText: "Under {platform}: kan der kun stå én værdi, og den er allerede i brug. Kopiér disse poster ind i din egen liste (eller flyt dem dertil).",
    ownEntries: "{n} egne poster",
    cstatus: { ok: "Din ihc-opsætning er fundet", no_ihc: "Fandt ingen ihc-opsætning", ambiguous: "Kunne ikke afgøre hvilken controller", unknown: "Kunne ikke kontrolleres" },
    pstate: { wired: "Koblet på", missing: "Mangler", inline: "Egne poster her", other_include: "Peger på anden fil", wrong_dir: "Peger på hele mappen" },
    prob_no_configuration: "Fandt ikke configuration.yaml i konfigurationsmappen.",
    prob_no_ihc: "Fandt ingen ihc:-opsætning i configuration.yaml eller i de filer, den henviser til (også packages).",
    prob_ihc_empty: "ihc: findes, men indeholder ingen controller.",
    prob_ambiguous_controller: "Der er {count} controllere i opsætningen, og jeg kan ikke afgøre, hvilken ViewMyIHC bruger (url'en står i en !secret). Indsæt linjerne under den rigtige.",
    prob_url_not_literal: "Controllerens url står i en !secret, så jeg kan ikke bekræfte, at det er den rigtige controller (secrets læses ikke).",
    prob_url_differs: "Url'en i opsætningen ({url}) er ikke den controller, Home Assistant er forbundet til ({controller}).",
    prob_not_wired: "{platform} er ikke koblet på.",
    prob_platform_taken: "{platform}: dine egne indstillinger bruger allerede denne nøgle ({count} poster).",
    taken_inline: "De står direkte i filen.", taken_other_include: "Nøglen peger på en anden fil ({include}).", taken_wrong_dir: "Nøglen peger på hele ViewMyIHC-mappen, som indeholder alle fire filer – det giver forkerte lister.",
    prob_duplicate_id: "{platform} med id {id} findes både i din egen opsætning og i ViewMyIHC – Home Assistant afviser den ene som dublet.",
    prob_auto_setup_on: "auto_setup er slået til (standard). Opretter den automatisk samme ressource, får du en dublet; sæt auto_setup: false, hvis du kun vil bruge manuelle poster.",
    prob_include_missing: "Henvisningen peger på {path}, som ikke findes.", prob_parse_error: "YAML-fejl: {error}",
    prob_outside_config: "En henvisning uden for konfigurationsmappen blev ikke fulgt ({path}).",
    prob_unreadable: "Kunne ikke læse {path}: {error}", prob_file_too_large: "{path} er for stor til at blive gennemgået.", prob_too_many_files: "For mange filer (grænse {limit}); gennemgangen blev afkortet.",
    refreshAdmin: "Opdater", updatedAt: "Opdateret kl. {time}",
    adminUpdating: "Viser gemt udgave fra kl. {time} – henter seneste værdier fra controlleren …",
    adminFirstLoad: "Henter indstillinger fra controlleren …",
    adminUptodate: "Opdateret – ingen ændringer", adminFetched: "Hentet fra controlleren",
    adminChanges: "{n} ændring(er) fundet siden den gemte udgave fra kl. {time}",
    adminPartial: "{n} kort kunne ikke opdateres – viser den gemte udgave",
    adminFailed: "Kunne ikke hente fra controlleren – viser gemt udgave fra kl. {time}",
    adminStale: "Kunne ikke opdateres, viser gemt udgave",
    changedChip: "{n} ændret", removedItems: "Fjernet", wasValue: "Før: {old}", newValue: "Ny", clearMarks: "Ryd markeringer",
    versionTitle: "Genstart Home Assistant",
    versionText: "Panelet (version {panel}) og integrationens Python-del (version {backend}) passer ikke sammen. Home Assistant indlæser integrationen ved opstart, så efter en opdatering skal HA genstartes helt (ikke kun siden genindlæses).",
    versionOld: "ældre end 0.2.0",
    readOnly: "Ændringer gemmes direkte på controlleren. Kun de felter, du retter, ændres – resten sendes uændret tilbage.",
    on: "Til", off: "Fra", resources: "ressourcer", blocks: "funktionsblokke", products: "produkter",
    modified: "Ændret", toMe: "Til", fromMe: "Fra", scene: "Scene", jump: "Gå til",
    adminError: "Kunne ikke læses", empty: "Ingen data", unit: "stk.",
    kind: { bool: "Til/fra", temperature: "Temperatur", time: "Tid", timer: "Timer", timertime: "Timertid",
      enum: "Valg", integer: "Heltal", weekday: "Ugedag", date: "Dato", scene: "Scene", unknown: "Ukendt" },
    cat: { group: "Lokalitet", product: "Produkt", functionblock: "Funktionsblok", section: "Gruppe",
      program: "Program", resource: "Ressource" },
  },
  en: {
    title: "ViewMyIHC", project: "Project", admin: "Administration", refresh: "Refresh",
    all: "All", installation: "Installation", programs: "Programs",
    search: "Search by name or ID …", loading: "Loading project from the controller …",
    copied: "Copied", copy: "Copy ID", noResults: "No results", id: "ID", hex: "Hex",
    path: "Location", note: "Note", values: "Properties", links: "Connections", current: "Current value",
    noSelection: "Select an item in the tree", close: "Close",
    noIhcTitle: "The IHC integration is not set up",
    noIhcText: "ViewMyIHC uses the connection of Home Assistant's built-in IHC integration. Configure it in configuration.yaml (ihc:) and restart, then the project shows up here.",
    errorTitle: "Could not read from the controller", retry: "Try again",
    entitiesTitle: "Entities in the ihc integration", inYaml: "in your YAML ({file}:{line})",
    entitiesLead: "Every entity the ihc integration has created (from your YAML or auto setup), plus entries in your YAML that wait for a restart. Watch the state right here.",
    entSearch: "Search by name, entity or id …", allTypes: "All", showInTree: "Show in tree", entNone: "No entities found.",
    noList: "No list yet", entryCount: "{n} entries",
    createYamlLead: "ViewMyIHC does not create the entity itself. You get the YAML entry to paste into your own ihc setup, and we check whether it exists already.",
    nameHelp: "Optional. Without a name the integration uses ihc_{id}.", optionsFor: "Settings for {platform}",
    livePreview: "YAML entry", makeYaml: "Create YAML", yourEntry: "Your YAML entry", copyYaml: "Copy YAML", back: "Back",
    step1: "Copy the entry.", step2: "Paste it into your ihc setup at the place shown.", stepRestart: "Restart Home Assistant (ihc reads its setup at startup).",
    verifyBtn: "Check if it is inserted", verifyFoundYaml: "Found in your YAML ({file}:{line}) – restart Home Assistant and the entity is created.",
    verifyFoundEntity: "Exists in ihc: {entity}.", verifyNone: "Not found yet – paste the entry and check again.",
    whereAppend: "Insert in {file} directly after line {line}", whereKey: " (under {platform}: in {kfile}:{kline}).",
    whereAddKey: "Insert in {file} directly after line {line}. This creates the key {platform}: under your controller.",
    whereNewFile: "Create a new .yaml file in the folder {dir} with this content (the folder is loaded with !include_dir_merge_list).",
    whereManual: "I could not follow your setup automatically. Put the entry as an item under {platform}: below your controller in the ihc setup.",
    existsTitle: "Already exists in the ihc integration", existsYaml: "in your YAML ({file}:{line}), waiting for a restart", disabledTag: "disabled",
    madeHere: "created in ViewMyIHC", openEntity: "Open the entity", takenBadge: "Exists", haChipTitle: "Exists in ihc: {list}",
    existsBlocked: "A {platform} entity already exists for this resource ({entity}). Home Assistant would reject a duplicate.",
    existsBlockedAll: "Already exists: {list}. Types that already exist cannot be created again (Home Assistant rejects duplicates), but you can pick another type.",
    existsOther: "An entity of another type already exists: {list}. You can create an extra one, but check that it is intended.",
    checkTitle: "Setup check", checkAgain: "Check again", checking: "Checking …",
    checkReadOnly: "Read only – ViewMyIHC never changes your files and does not read secrets.yaml.",
    scannedFiles: "{n} files scanned", wiredOk: "Connected – restart Home Assistant and the entity shows up",
    seeEntitiesTab: "See the Entities tab for details.",
    foundIn: "Your ihc setup is defined in {file} line {line}.", controllerIn: "The controller is in {file} line {line}.",
    insertTitle: "Insert these lines", insertTitleLater: "Prepare for later (only needed once you create entities)", insertHere: "In {file} directly after line {line} (indentation: {indent} spaces):",
    mergeTitle: "Merge {platform} by hand", mergeText: "Only one value can sit under {platform}:, and it is already in use. Copy these entries into your own list (or move them there).",
    ownEntries: "{n} own entries",
    cstatus: { ok: "Your ihc setup was found", no_ihc: "No ihc setup found", ambiguous: "Could not tell which controller", unknown: "Could not be checked" },
    pstate: { wired: "Connected", missing: "Missing", inline: "Own entries here", other_include: "Points to another file", wrong_dir: "Points to the whole folder" },
    prob_no_configuration: "configuration.yaml was not found in the configuration folder.",
    prob_no_ihc: "No ihc: setup found in configuration.yaml or the files it refers to (packages included).",
    prob_ihc_empty: "ihc: exists but contains no controller.",
    prob_ambiguous_controller: "The setup has {count} controllers and I cannot tell which one ViewMyIHC uses (the url is in a !secret). Insert the lines under the right one.",
    prob_url_not_literal: "The controller's url is in a !secret, so I cannot confirm it is the right controller (secrets are not read).",
    prob_url_differs: "The url in the setup ({url}) is not the controller Home Assistant is connected to ({controller}).",
    prob_not_wired: "{platform} is not connected.",
    prob_platform_taken: "{platform}: your own configuration already uses this key ({count} entries).",
    taken_inline: "They are written directly in the file.", taken_other_include: "The key points to another file ({include}).", taken_wrong_dir: "The key points to the whole ViewMyIHC folder, which holds all four files – that gives wrong lists.",
    prob_duplicate_id: "{platform} with id {id} exists both in your own setup and in ViewMyIHC – Home Assistant rejects one of them as a duplicate.",
    prob_auto_setup_on: "auto_setup is on (the default). If it also creates the same resource you get a duplicate; set auto_setup: false if you only want manual entries.",
    prob_include_missing: "The reference points to {path}, which does not exist.", prob_parse_error: "YAML error: {error}",
    prob_outside_config: "A reference outside the configuration folder was not followed ({path}).",
    prob_unreadable: "Could not read {path}: {error}", prob_file_too_large: "{path} is too large to scan.", prob_too_many_files: "Too many files (limit {limit}); the scan was cut short.",
    refreshAdmin: "Update", updatedAt: "Updated at {time}",
    adminUpdating: "Showing the saved copy from {time} – fetching the latest values from the controller …",
    adminFirstLoad: "Reading the settings from the controller …",
    adminUptodate: "Up to date – no changes", adminFetched: "Read from the controller",
    adminChanges: "{n} change(s) found since the saved copy from {time}",
    adminPartial: "{n} card(s) could not be updated – showing the saved copy",
    adminFailed: "Could not read from the controller – showing the saved copy from {time}",
    adminStale: "Could not be updated, showing the saved copy",
    changedChip: "{n} changed", removedItems: "Removed", wasValue: "Before: {old}", newValue: "New", clearMarks: "Clear marks",
    versionTitle: "Restart Home Assistant",
    versionText: "The panel (version {panel}) and the integration's Python part (version {backend}) do not match. Home Assistant loads the integration at startup, so after an update HA must be fully restarted (reloading the page is not enough).",
    versionOld: "older than 0.2.0",
    readOnly: "Changes are saved directly on the controller. Only the fields you change are changed – the rest is sent back as it was.",
    on: "On", off: "Off", resources: "resources", blocks: "function blocks", products: "products",
    modified: "Modified", toMe: "To", fromMe: "From", scene: "Scene", jump: "Go to",
    adminError: "Could not be read", empty: "No data", unit: "pcs.",
    kind: { bool: "On/off", temperature: "Temperature", time: "Time", timer: "Timer", timertime: "Timer time",
      enum: "Choice", integer: "Integer", weekday: "Weekday", date: "Date", scene: "Scene", unknown: "Unknown" },
    cat: { group: "Location", product: "Product", functionblock: "Function block", section: "Group",
      program: "Program", resource: "Resource" },
  },
};


const I18N_EXTRA = {
  da: {
    entities: "Entiteter", createEntity: "Opret entitet", editEntity: "Rediger entitet", entityType: "Entitetstype",
    suggested: "Foreslået", name: "Navn", nameIdeas: "Forslag", position: "Rum (IHC-position)",
    positionHelp: "Gemmes som IHC-attributten ‘position’ på entiteten.", area: "Område i Home Assistant",
    areaHelp: "Entiteten lægges i området, første gang Home Assistant opretter den.", noArea: "Intet område",
    cancel: "Annuller", create: "Opret", save: "Gem", saving: "Gemmer …", idLocked: "Ressource-ID (kan ikke ændres)",
    inverting: "Inverteret (til/fra byttes om)", deviceClass: "Sensortype", noClass: "Ingen",
    unit: "Enhed", dimmable: "Dæmpbar (ressourcen er et lysniveau)", onId: "Tænd-ID (pulseres)", offId: "Sluk-ID (pulseres)",
    pulseHelp: "Valgfrit: en anden ressource, der pulseres i stedet for at sætte værdien.",
    preview: "Forhåndsvisning af det, der skrives", file: "Fil",
    savedTitle: "Entiteten er gemt", restartTitle: "Genstart Home Assistant for at aktivere",
    restartText: "Den indbyggede IHC-integration læser sin opsætning ved opstart. ViewMyIHC har skrevet entiteten til en fil, og den dukker op efter næste genstart.",
    wireTitle: "Første gang: koble filerne på", wireText: "Tilføj disse linjer under din controller i configuration.yaml (én gang). Resten sker automatisk.",
    copySnippet: "Kopiér", close: "Luk", existingTitle: "Findes allerede", active: "Aktiv", pending: "Afventer genstart",
    edit: "Rediger", remove: "Fjern", removeConfirm: "Fjern denne entitet? Den forsvinder efter næste genstart.",
    noEntities: "Du har ikke oprettet nogen entiteter endnu. Vælg en ressource i træet og tryk ‘Opret entitet’.",
    setupTitle: "Opsætning", filesWritten: "ViewMyIHC skriver disse filer (ret dem ikke i hånden):",
    unsupported: "Denne type kan ikke bruges i den indbyggede IHC-integration endnu.",
    required: "Skal udfyldes", hasEntity: "Har entitet", platform: { binary_sensor: "Binær sensor", light: "Lys", sensor: "Sensor", switch: "Kontakt" },
    modules: "Moduler", log: "Log", versions: "Versioner", internalLink: "Intern indstilling eller program – vises ikke i træet",
    dlLoading: "Henter dataline-adresser fra controlleren …", dlUsed: "{used} af {all} i brug", dlLine: "Linje {n}", dlPickTitle: "Vælg en adresse", dlPick: "Klik på en adresse til venstre for at se ressourcen, styre den og se dens forbindelser.", dlChecking: "Henter seneste fra controlleren …", dlChanged: "Moduler opdateret fra controlleren",
    dlSavedAt: "Controllerens adresser hentet kl. {time}", dlNoModule: "intet modul angivet i projektet", dlAddress: "adresse",
    dlOutsideChip: "{n} uden for modulet", dlOutside: "Brugt i projektet, men modulet på linjen har ikke denne plads",
    dlCtlError: "Controlleren svarede ikke – ledige pladser vises uden ressource-id.", dlInputs: "Dataline-indgange", dlOutputs: "Dataline-udgange", dlFree: "Ledig",
    dlLead: "Hver datalinje med det modul, projektet har på den (type og tavle), og kun de pladser modulet har – fx 8 på et 230 V-indgangsmodul, selv om linjen har 16 adresser. Klik på en plads for at se og styre ressourcen til højre. Stiplet: i brug, men ikke forbundet til noget; rød: brugt på en plads modulet ikke har.",
    log_userlog: "Controllerlog", log_messages: "SMS og e-mail", log_monitor: "Live-monitor", logSearch: "Filtrér …",
    logLead: "Controllerens egen log, som IHC Administrator viser den (fx lavt batteri, login og fejl). Linjer om batteri og fejl er fremhævet.",
    logEmpty: "Loggen er tom.", logNewestFirst: "Vend rækkefølgen", logOldestFirst: "Oprindelig rækkefølge",
    msgSent: "Sendte beskeder (SMS og e-mail)", msgNone: "Ingen.", msgControl: "Styring via e-mail/SMS",
    msgControlLead: "Kommandoer controlleren har modtaget som e-mail eller SMS, og hvad den gjorde med dem.",
    msgControlOff: "E-mail-/SMS-styring er slået fra på controlleren, så der føres ingen log. Den slås til under Administration → E-mail kontrol.",
    logClear: "Tøm", logClearAsk: "Tøm loggen på controlleren? Det kan ikke fortrydes.", logCleared: "Loggen er tømt",
    colTime: "Tid", colType: "Type", colTo: "Modtager", colSubject: "Emne", colDelivered: "Leveret", colFrom: "Afsender", colCommand: "Kommando", colResult: "Handling",
    monLead: "Viser hver ændring af en værdi i projektet, mens det sker: tryk, udgange, indstillinger – med tid, navn og før/efter.",
    monNote: "Monitoren lytter med på ihc-integrationens egne meddelelser fra controlleren, så den stjæler ingenting fra dine entiteter. Når den er startet, kører den til næste genstart af Home Assistant (de seneste 2000 ændringer gemmes).",
    monStart: "Start monitor", monStarting: "Starter …", monPause: "Pause", monResume: "Fortsæt", monClear: "Ryd",
    monWatching: "{n} ressourcer overvåges siden {time}. Klik på en række for at se den i træet.", monChange: "Før → efter", monNone: "Ingen ændringer endnu.",
    bkLead: "Hver gang projektet på controlleren ændres, gemmer ViewMyIHC en kopi (de seneste 30). Kopierne ligger i Home Assistants .storage-mappe og indeholder hele projektet – også kundedata og SMS-modemets PIN-kode.",
    bkTitle: "Gemte projekter", bkSaved: "Gemt", bkSize: "Størrelse", bkNone: "Ingen endnu – den første gemmes, når projektet hentes fra controlleren.",
    bkCompare: "Hvad er ændret", bkFrom: "Fra", bkTo: "Til", bkSame: "Ingen forskel på det, panelet viser.", bkMore: "… og {n} mere",
    bkAdded: "Tilføjet", bkRemoved: "Fjernet", bkChanged: "Ændret",
    covBlocks: "Funktionsblokke", covTitle: "Dækning", covSummary: "{n} af {all} har en entitet", covMissing: "Uden entitet", covUnlinked: "Ikke forbundet", covNoLinks: "ingen forbindelser",
    covLead: "Alle ressourcer i projektet, og om de findes som entitet i Home Assistant. ‘Ikke forbundet’ er ressourcer uden forbindelser i projektet – fx ubrugte tryk.",
    covTag: { dataline_input: "Dataline-indgange", dataline_output: "Dataline-udgange", airlink_input: "Trådløse indgange", airlink_output: "Trådløse udgange" },
    covSection: { inputs: "Input", outputs: "Output", settings: "Indstillinger" },
    pressTitle: "Automation for kort, langt og dobbelt tryk", pressLong: "Langt tryk efter (ms)", pressDouble: "Dobbelt tryk inden for (ms)", pressMake: "Lav YAML",
    pressLead: "IHC melder kun ‘trykket’ og ‘sluppet’. Automationen måler selv trykket og skelner mellem kort, langt og dobbelt tryk; erstat de tre logbook-handlinger med dine egne.",
    pressNeedsSensor: "Kræver en binær sensor for tasten. Opret den først med ‘Opret entitet’ (type Binær sensor) og genstart Home Assistant.",
    pressHow: "Indsæt i Indstillinger → Automatiseringer → Ny → ⋮ → Redigér i YAML.",
    adminAuth: "Adgangskode for {user} – brugeren Home Assistant er logget ind på IHC med", adminAuthMissing: "Skriv adgangskoden for at gemme.",
    adminAuthWrong: "Forkert adgangskode – intet er ændret.", adminAuthLocked: "For mange forkerte forsøg – vent et par minutter.",
    adminAuthDelete: "Sletning kræver også adgangskoden herunder.",
    pwRepeat: "Gentag adgangskode", pwMatch: "✓ Adgangskoderne er ens", pwMismatch: "Adgangskoderne er ikke ens",
    adminTitle: { system: "System", time: "Tid og sommertid", local_time: "Lokal tid", uptime: "Oppetid", users: "Brugere", network: "Netværk",
      dns: "DNS", web_access: "Webadgang", smtp: "E-mail (SMTP)", email_control: "E-mail-kontrol", sms_modem: "SMS-modem",
      sms_status: "SMS-modem: status", sms_info: "SMS-modem: enhed" },
    adminManage: "Administrér", adminSaved: "Gemt på controlleren", adminKeepPassword: "uændret",
    adminNeedsConfirm: "Ændringen kan afbryde forbindelsen til controlleren. Bekræft for at gemme.",
    adminConfirmBox: "Jeg forstår, at forbindelsen kan blive afbrudt, og at ihc-opsætningen i Home Assistant skal rettes, hvis adressen ændres",
    adminNetWarn: "Ny IP-adresse eller port: controlleren skal måske genstartes, og url'en i din ihc-opsætning skal rettes, ellers mister Home Assistant forbindelsen.",
    adminWebWarn: "Treeview og Administrator på lokalnettet kan ikke slås fra her – Home Assistant og IHC Administrator bruger dem.",
    adminLocked: "Bruges af Home Assistant / IHC Administrator", adminLan: "Lokalnet", adminWan: "Internet",
    adminSetClock: "Sæt uret til nu", adminClockConfirm: "Sæt controllerens ur til Home Assistants tid nu?",
    adminNewUser: "Ny bruger", adminHaUser: "bruges af Home Assistant",
    adminHaUserPw: "Home Assistant logger ind med denne bruger: skift adgangskoden i IHC Administrator og i ihc-opsætningen samtidig.",
    adminPasswordHelp: "Lad adgangskoden stå tom for at beholde den nuværende.", adminDeleteUser: "Slet brugeren ‘{user}’ på controlleren?",
    settings: "Indstillinger", setSaved: "Indstillingerne er gemt", setConnTitle: "Forbindelsen til controlleren",
    setConnLead: "Når IHC-controlleren genstarter, kan ihc-integrationen gå i stå: du kan stadig tænde og slukke fra Home Assistant, men tilstandene opdateres ikke før en genstart af Home Assistant. Det skyldes, at integrationen venter på svar uden tidsgrænse. Med en tidsgrænse ender et svar, der aldrig kommer, med en fejl, og så genopretter integrationen selv forbindelsen.",
    setTimeout: "Brug en tidsgrænse på ihc-integrationens forbindelse", setSeconds: "Tidsgrænse i sekunder ({min}–{max})",
    setActive: "Aktiv: {s} sekunder", setInactive: "Ikke aktiv", setNoController: "Ingen IHC-controller fundet.",
    setWhy: "Hvad ændres der?",
    setWhyText: "ViewMyIHC sætter tidsgrænsen på den forbindelse, ihc-integrationen allerede har (ikke globalt, og ikke i dens filer). Controlleren svarer normalt inden for 10 sekunder, så tidsgrænsen rammer kun et kald, der er gået i stå. Slås den fra, er forbindelsen præcis som før. Er integrationen allerede gået i stå, når den slås til, kræver det stadig én genstart af Home Assistant.",
    reports: "Rapporter", repLead: "Lavet ud fra projektet, som det er på controlleren nu – som controllerens egne rapporter.",
    rep_installation: "Installationsdokumentation", rep_installation_lead: "Ind- og udgange med kabler, moduler og produkter",
    rep_function: "Funktionsdokumentation", rep_function_lead: "Til beboerne: hvad hver tast gør, pr. lokalitet",
    rep_functionblocks: "Funktionsblokdokumentation", rep_functionblocks_lead: "Hver funktionsblok med ind-/udgange, indstillinger og startværdier",
    repOnlyMarked: "Kun produkter, der er markeret til slutbrugerrapporten i IHC Visual", repPrint: "Udskriv / gem som PDF", repDownload: "Hent som HTML",
    repPopup: "Browseren blokerede vinduet – tillad pop-op-vinduer for Home Assistant.", repGenerated: "Udskrevet {time}",
    repTerminal: "Klemme", repProduct: "Produkt", repLocation: "Lokalitet", repPosition: "Placering", repTag: "Id-kode", repCableType: "Kabeltype",
    repCableNo: "Kabelnummer", repPowerGroup: "Lysgruppe", repColour: "Ledning", repIn: "Indgang", repOut: "Udgang", repLine: "Datalinje",
    repModuleType: "Modultype", repInModules: "Indgangsmoduler", repOutModules: "Udgangsmoduler", repComponent: "Komponent", repSerial: "Serienummer",
    repCustomer: "Kunde", repInstaller: "Installatør", repAddress: "Adresse", repType: "Type", repInitial: "Startværdi", repOutputs: "Udgange",
    repNotUsed: "ikke i brug", repProducts: "Produkter", repNoModules: "Ingen moduler angivet i projektet.", repNone: "Ingen produkter.", repNoneMarked: "Ingen produkter er markeret til slutbrugerrapporten i IHC Visual – slå filteret fra for at se alle.",
    phone: "Telefon", email: "E-mail",
    weekdays: { monday: "Mandag", tuesday: "Tirsdag", wednesday: "Onsdag", thursday: "Torsdag", friday: "Fredag", saturday: "Lørdag", sunday: "Søndag" },
    map: "Kort", mapSearch: "Find produkt …", mapZoomIn: "Zoom ind", mapZoomOut: "Zoom ud", mapHome: "Controlleren og modulerne",
    mapAll: "Hele anlægget", mapAirlink: "Trådløst (Airlink)", mapNoModule: "intet modul angivet", mapIn: "Ind", mapOut: "Ud",
    mapLines: "linjer", mapHits: "{n} fundet – Enter for næste", mapUnwired: "{n} produkter uden datalinjeadresse (fx temperaturfølere) vises ikke.",
    scTitle: "Opsætning af beskeder og styring (IHC SceneDesign)",
    scLead: "Hvem der får besked, når en ressource ændrer sig, og hvem der kan styre controlleren med e-mail eller SMS. Det er sat op i IHC SceneDesign og ligger i dens projekt på controlleren.",
    scNotifications: "Beskeder ved hændelser", scControls: "Styring via e-mail/SMS", scResource: "Ressource", scWhen: "Når", scTo: "Modtagere",
    scMessage: "Besked", scDoes: "Gør", scAuth: "Godkendelse", scFrom: "Tilladte afsendere", scReply: "Svar", scConfirmTo: "Bekræftes af",
    scAnyone: "Alle, der kender kommandoen", scSlot: "Nummer {n}",
    scEditNote: "Rettes i IHC SceneDesign. Redigering herfra kommer, når upload af scene-projektet er afprøvet sammen med dig.",
    scEvent: { inactive_to_active_event: "Går til", active_to_inactive_event: "Går fra" },
    scAction: { off_to_on_action: "Tænder", on_to_off_action: "Slukker", pulse_action: "Pulser" },
    scAuthType: { direct_control: "Direkte", sender_based: "Kun kendte afsendere", three_way: "3-vejs bekræftelse" },
    bkKind_ihc: "IHC-projekt", bkKind_scene: "Scene-projekt (SceneDesign)", bkSceneScenes: "Scener",
    bkSceneLead: "SceneDesigns projekt med scener, beskeder og styring via e-mail/SMS. En kopi gemmes, hver gang det ændres på controlleren (de seneste 30), og kan hentes som .icz og åbnes i IHC SceneDesign.",
    control: "Styring", ctlInitial: "Startværdi", set: "Sæt", seconds: "sek.",
    ctlLoading: "Henter værdier fra controlleren …", hold: "Hold for at skifte", holding: "Holdes – slip for at skifte tilbage",
    holdHelp: "Skifter værdien, så længe knappen holdes nede (som mellemrumstasten i ServiceView). På mobil: hold fingeren stille et øjeblik – et hurtigt tryk eller en scroll gør ingenting. Mister panelet forbindelsen, skifter Home Assistant selv tilbage efter få sekunder.",
    ctlInitialHelp: "Den værdi controlleren starter med efter genstart eller strømsvigt. Sendes projektet igen fra IHC Visual, gælder startværdien i projektfilen.",
    notEditable: "Typen {type} kan ikke ændres her.", confirmInitial: "Sæt startværdien for ‘{name}’ til {value}?\n\nControlleren bruger den, næste gang den starter.",
    badValue: "Ugyldig værdi – tjek feltet.", savedValue: "Værdien er sat",savedInitial: "Startværdien er sat", iniProject: "Startværdi (projektfil)",
    platformHelp: { binary_sensor: "Til/fra-tilstand (tryk, bevægelse, døre …)", light: "Tænd/sluk eller dæmpbart lys",
      sensor: "Tal (temperatur, fugtighed, lux …)", switch: "Kontakt der kan tændes og slukkes" },
  },
  en: {
    entities: "Entities", createEntity: "Create entity", editEntity: "Edit entity", entityType: "Entity type",
    suggested: "Suggested", name: "Name", nameIdeas: "Ideas", position: "Room (IHC position)",
    positionHelp: "Stored as the IHC ‘position’ attribute on the entity.", area: "Area in Home Assistant",
    areaHelp: "The entity is placed in this area the first time Home Assistant creates it.", noArea: "No area",
    cancel: "Cancel", create: "Create", save: "Save", saving: "Saving …", idLocked: "Resource ID (cannot be changed)",
    inverting: "Inverted (on/off swapped)", deviceClass: "Sensor type", noClass: "None",
    unit: "Unit", dimmable: "Dimmable (the resource is a light level)", onId: "On ID (pulsed)", offId: "Off ID (pulsed)",
    pulseHelp: "Optional: another resource that is pulsed instead of setting the value.",
    preview: "Preview of what will be written", file: "File",
    savedTitle: "The entity was saved", restartTitle: "Restart Home Assistant to activate",
    restartText: "The built-in IHC integration reads its setup at startup. ViewMyIHC wrote the entity to a file and it shows up after the next restart.",
    wireTitle: "First time: connect the files", wireText: "Add these lines under your controller in configuration.yaml (once). Everything else happens automatically.",
    copySnippet: "Copy", close: "Close", existingTitle: "Already exists", active: "Active", pending: "Waiting for restart",
    edit: "Edit", remove: "Remove", removeConfirm: "Remove this entity? It disappears after the next restart.",
    noEntities: "You have not created any entities yet. Select a resource in the tree and press ‘Create entity’.",
    setupTitle: "Setup", filesWritten: "ViewMyIHC writes these files (do not edit them by hand):",
    unsupported: "This type cannot be used with the built-in IHC integration yet.",
    required: "Required", hasEntity: "Has entity", platform: { binary_sensor: "Binary sensor", light: "Light", sensor: "Sensor", switch: "Switch" },
    modules: "Modules", log: "Log", versions: "Versions", internalLink: "Internal setting or program – not shown in the tree",
    dlLoading: "Reading dataline addresses from the controller …", dlUsed: "{used} of {all} in use", dlLine: "Line {n}", dlPickTitle: "Pick an address", dlPick: "Click an address on the left to see the resource, control it and see its links.", dlChecking: "Reading the latest from the controller …", dlChanged: "Modules updated from the controller",
    dlSavedAt: "Controller addresses read at {time}", dlNoModule: "no module entered in the project", dlAddress: "address",
    dlOutsideChip: "{n} outside the module", dlOutside: "Used in the project, but the module on this line has no such position",
    dlCtlError: "The controller did not answer – free positions are shown without a resource id.", dlInputs: "Dataline inputs", dlOutputs: "Dataline outputs", dlFree: "Free",
    dlLead: "Every dataline line with the module the project puts on it (type and panel), and only the positions that module has – 8 on a 230 V input module, for example, although the line has 16 addresses. Click a position to see and control the resource on the right. Dashed: in use but linked to nothing; red: used on a position the module does not have.",
    log_userlog: "Controller log", log_messages: "SMS and e-mail", log_monitor: "Live monitor", logSearch: "Filter …",
    logLead: "The controller's own log as IHC Administrator shows it (low battery, logins, errors). Lines about batteries and errors are highlighted.",
    logEmpty: "The log is empty.", logNewestFirst: "Reverse the order", logOldestFirst: "Original order",
    msgSent: "Sent messages (SMS and e-mail)", msgNone: "None.", msgControl: "Control by e-mail/SMS",
    msgControlLead: "Commands the controller received as e-mail or SMS, and what it did with them.",
    msgControlOff: "E-mail/SMS control is switched off on the controller, so no log is kept. Switch it on under Administration → E-mail control.",
    logClear: "Empty", logClearAsk: "Empty this log on the controller? This cannot be undone.", logCleared: "The log is empty",
    colTime: "Time", colType: "Type", colTo: "Recipient", colSubject: "Subject", colDelivered: "Delivered", colFrom: "Sender", colCommand: "Command", colResult: "Action",
    monLead: "Shows every change of a value in the project as it happens: buttons, outputs, settings – with time, name and before/after.",
    monNote: "The monitor listens to the ihc integration's own notifications from the controller, so it takes nothing away from your entities. Once started it runs until Home Assistant restarts (the latest 2000 changes are kept).",
    monStart: "Start monitor", monStarting: "Starting …", monPause: "Pause", monResume: "Resume", monClear: "Clear",
    monWatching: "{n} resources watched since {time}. Click a row to see it in the tree.", monChange: "Before → after", monNone: "No changes yet.",
    bkLead: "Every time the project on the controller changes, ViewMyIHC keeps a copy (the latest 30). The copies are in Home Assistant's .storage folder and hold the whole project – customer data and the SMS modem's PIN code included.",
    bkTitle: "Saved projects", bkSaved: "Saved", bkSize: "Size", bkNone: "None yet – the first one is saved when the project is read from the controller.",
    bkCompare: "What changed", bkFrom: "From", bkTo: "To", bkSame: "No difference in what the panel shows.", bkMore: "… and {n} more",
    bkAdded: "Added", bkRemoved: "Removed", bkChanged: "Changed",
    covBlocks: "Function blocks", covTitle: "Coverage", covSummary: "{n} of {all} have an entity", covMissing: "Without entity", covUnlinked: "Not linked", covNoLinks: "no links",
    covLead: "Every resource in the project, and whether it exists as an entity in Home Assistant. ‘Not linked’ are resources without links in the project – unused buttons, for example.",
    covTag: { dataline_input: "Dataline inputs", dataline_output: "Dataline outputs", airlink_input: "Wireless inputs", airlink_output: "Wireless outputs" },
    covSection: { inputs: "Inputs", outputs: "Outputs", settings: "Settings" },
    pressTitle: "Automation for short, long and double press", pressLong: "Long press after (ms)", pressDouble: "Double press within (ms)", pressMake: "Make YAML",
    pressLead: "IHC only reports ‘pressed’ and ‘released’. The automation times the press itself and tells short, long and double presses apart; replace the three logbook actions with your own.",
    pressNeedsSensor: "Needs a binary sensor for the button. Create it first with ‘Create entity’ (type Binary sensor) and restart Home Assistant.",
    pressHow: "Paste into Settings → Automations → New → ⋮ → Edit in YAML.",
    adminAuth: "Password of {user} – the user Home Assistant is logged in to IHC with", adminAuthMissing: "Enter the password to save.",
    adminAuthWrong: "Wrong password – nothing was changed.", adminAuthLocked: "Too many wrong attempts – wait a few minutes.",
    adminAuthDelete: "Deleting also needs the password below.",
    pwRepeat: "Repeat password", pwMatch: "✓ The passwords match", pwMismatch: "The passwords do not match",
    adminTitle: { system: "System", time: "Time and daylight saving", local_time: "Local time", uptime: "Uptime", users: "Users",
      network: "Network", dns: "DNS", web_access: "Web access", smtp: "E-mail (SMTP)", email_control: "E-mail control",
      sms_modem: "SMS modem", sms_status: "SMS modem: status", sms_info: "SMS modem: device" },
    adminManage: "Manage", adminSaved: "Saved on the controller", adminKeepPassword: "unchanged",
    adminNeedsConfirm: "This change can cut the connection to the controller. Confirm to save.",
    adminConfirmBox: "I understand the connection can be lost, and that the ihc setup in Home Assistant must be changed if the address changes",
    adminNetWarn: "New IP address or port: the controller may need a restart, and the url in your ihc setup must be changed, or Home Assistant loses the connection.",
    adminWebWarn: "Treeview and Administrator on the local network cannot be switched off here – Home Assistant and IHC Administrator use them.",
    adminLocked: "Used by Home Assistant / IHC Administrator", adminLan: "Local network", adminWan: "Internet",
    adminSetClock: "Set the clock to now", adminClockConfirm: "Set the controller's clock to Home Assistant's time now?",
    adminNewUser: "New user", adminHaUser: "used by Home Assistant",
    adminHaUserPw: "Home Assistant logs in with this user: change the password in IHC Administrator and in the ihc setup at the same time.",
    adminPasswordHelp: "Leave the password empty to keep the current one.", adminDeleteUser: "Delete the user ‘{user}’ on the controller?",
    settings: "Settings", setSaved: "Settings saved", setConnTitle: "The connection to the controller",
    setConnLead: "When the IHC controller restarts, the ihc integration can get stuck: you can still switch things from Home Assistant, but states stop updating until Home Assistant restarts. The integration waits for answers without a time limit. With a time limit, an answer that never comes ends with an error, and the integration restores the connection by itself.",
    setTimeout: "Use a time limit on the ihc integration's connection", setSeconds: "Time limit in seconds ({min}–{max})",
    setActive: "Active: {s} seconds", setInactive: "Not active", setNoController: "No IHC controller found.",
    setWhy: "What is changed?",
    setWhyText: "ViewMyIHC puts the time limit on the connection the ihc integration already has (not globally, and not in its files). The controller normally answers within 10 seconds, so the limit only hits a call that is stuck. Switched off, the connection is exactly as before. If the integration is already stuck when this is switched on, it still takes one restart of Home Assistant.",
    reports: "Reports", repLead: "Made from the project as it is on the controller now – like the controller's own reports.",
    rep_installation: "Installation documentation", rep_installation_lead: "Inputs and outputs with cables, modules and products",
    rep_function: "Function documentation", rep_function_lead: "For the residents: what each button does, per location",
    rep_functionblocks: "Function block documentation", rep_functionblocks_lead: "Each function block with inputs/outputs, settings and initial values",
    repOnlyMarked: "Only products marked for the end-user report in IHC Visual", repPrint: "Print / save as PDF", repDownload: "Download as HTML",
    repPopup: "The browser blocked the window – allow pop-ups for Home Assistant.", repGenerated: "Printed {time}",
    repTerminal: "Terminal", repProduct: "Product", repLocation: "Location", repPosition: "Position", repTag: "Id code", repCableType: "Cable type",
    repCableNo: "Cable number", repPowerGroup: "Power group", repColour: "Wire", repIn: "Input", repOut: "Output", repLine: "Dataline",
    repModuleType: "Module type", repInModules: "Input modules", repOutModules: "Output modules", repComponent: "Component", repSerial: "Serial number",
    repCustomer: "Customer", repInstaller: "Installer", repAddress: "Address", repType: "Type", repInitial: "Initial value", repOutputs: "Outputs",
    repNotUsed: "not used", repProducts: "Products", repNoModules: "No modules entered in the project.", repNone: "No products.", repNoneMarked: "No products are marked for the end-user report in IHC Visual – switch the filter off to see all.",
    phone: "Phone", email: "E-mail",
    weekdays: { monday: "Monday", tuesday: "Tuesday", wednesday: "Wednesday", thursday: "Thursday", friday: "Friday", saturday: "Saturday", sunday: "Sunday" },
    map: "Map", mapSearch: "Find product …", mapZoomIn: "Zoom in", mapZoomOut: "Zoom out", mapHome: "Controller and modules",
    mapAll: "Whole installation", mapAirlink: "Wireless (Airlink)", mapNoModule: "no module entered", mapIn: "In", mapOut: "Out",
    mapLines: "lines", mapHits: "{n} found – Enter for next", mapUnwired: "{n} products without a dataline address (e.g. temperature sensors) are not shown.",
    scTitle: "Messages and control setup (IHC SceneDesign)",
    scLead: "Who is told when a resource changes, and who may control the controller by e-mail or SMS. It is set up in IHC SceneDesign and kept in its project on the controller.",
    scNotifications: "Messages on events", scControls: "Control by e-mail/SMS", scResource: "Resource", scWhen: "When", scTo: "Recipients",
    scMessage: "Message", scDoes: "Does", scAuth: "Authorisation", scFrom: "Allowed senders", scReply: "Reply", scConfirmTo: "Confirmed by",
    scAnyone: "Anyone who knows the command", scSlot: "Number {n}",
    scEditNote: "Changed in IHC SceneDesign. Editing from here comes once uploading the scene project has been tested together with you.",
    scEvent: { inactive_to_active_event: "Turns on", active_to_inactive_event: "Turns off" },
    scAction: { off_to_on_action: "Switches on", on_to_off_action: "Switches off", pulse_action: "Pulses" },
    scAuthType: { direct_control: "Direct", sender_based: "Known senders only", three_way: "3-way confirmation" },
    bkKind_ihc: "IHC project", bkKind_scene: "Scene project (SceneDesign)", bkSceneScenes: "Scenes",
    bkSceneLead: "SceneDesign's project with scenes, messages and control by e-mail/SMS. A copy is kept every time it changes on the controller (the latest 30) and can be downloaded as .icz and opened in IHC SceneDesign.",
    control: "Control", ctlInitial: "Initial value", set: "Set", seconds: "s",
    ctlLoading: "Reading values from the controller …", hold: "Hold to change", holding: "Held – release to switch back",
    holdHelp: "Changes the value for as long as the button is held (like the space bar in ServiceView). On a phone: rest your finger for a moment – a quick tap or a scroll does nothing. If the panel loses its connection, Home Assistant switches back by itself after a few seconds.",
    ctlInitialHelp: "The value the controller starts with after a restart or power cut. If the project is sent again from IHC Visual, the initial value in the project file applies.",
    notEditable: "Type {type} cannot be changed here.", confirmInitial: "Set the initial value of ‘{name}’ to {value}?\n\nThe controller uses it the next time it starts.",
    badValue: "Invalid value – check the field.", savedValue: "Value set",savedInitial: "Initial value set", iniProject: "Initial value (project file)",
    platformHelp: { binary_sensor: "On/off state (buttons, motion, doors …)", light: "On/off or dimmable light",
      sensor: "Number (temperature, humidity, lux …)", switch: "Switch that can be turned on and off" },
  },
};
Object.assign(I18N.da, I18N_EXTRA.da);
Object.assign(I18N.en, I18N_EXTRA.en);

const PLATFORM_ICON = { binary_sensor: "mdi:radiobox-marked", light: "mdi:lightbulb-outline", sensor: "mdi:gauge", switch: "mdi:toggle-switch-outline" };

// the icon Home Assistant shows for a binary sensor of this class in its "on" state
const DEVICE_CLASS_ICON = {
  battery: "mdi:battery-outline", battery_charging: "mdi:battery-charging", carbon_monoxide: "mdi:smoke-detector-alert",
  cold: "mdi:snowflake", connectivity: "mdi:check-network-outline", door: "mdi:door-open", garage_door: "mdi:garage-open",
  gas: "mdi:alert-circle", heat: "mdi:fire", light: "mdi:brightness-7", lock: "mdi:lock-open", moisture: "mdi:water",
  motion: "mdi:motion-sensor", moving: "mdi:octagon", occupancy: "mdi:home", opening: "mdi:square-outline",
  plug: "mdi:power-plug", power: "mdi:power-plug", presence: "mdi:home", problem: "mdi:alert-circle",
  running: "mdi:play", safety: "mdi:alert-circle", smoke: "mdi:smoke-detector-variant-alert", sound: "mdi:music-note",
  tamper: "mdi:alert-circle", update: "mdi:package-up", vibration: "mdi:vibrate", window: "mdi:window-open",
};
const NO_CLASS_ICON = "mdi:radiobox-marked";

// wiring map geometry (SVG units)
const MAP = { ctrlW: 260, ctrlH: 420, modW: 320, modH: 112, modRoom: 70, gapCM: 300, gapMP: 300, prodW: 280, prodH: 76,
  prodGap: 16, colGap: 40, portGap: 15, blockGap: 70 };
// icons for LK products the controller has no picture of, by LK product number
const PRODUCT_ICON = {
  _0x2109: "mdi:magnet-on", _0x210a: "mdi:smoke-detector-variant", _0x210e: "mdi:motion-sensor", _0x210f: "mdi:motion-sensor",
  _0x2110: "mdi:weather-sunset", _0x2111: "mdi:dialpad", _0x2112: "mdi:shield-alert-outline", _0x2115: "mdi:battery-charging-outline",
  _0x2124: "mdi:thermometer", _0x2201: "mdi:power-socket-de", _0x2202: "mdi:ceiling-light-outline", _0x2203: "mdi:bullhorn-outline",
  _0x2204: "mdi:alarm-light-outline", _0x2209: "mdi:bell-ring-outline", _0x220a: "mdi:radiator", _0x220b: "mdi:pump",
  _0x220c: "mdi:fan", _0x2703: "mdi:electric-switch",
};
const REPORT_ICON = { installation: "mdi:cable-data", function: "mdi:gesture-tap-button", functionblocks: "mdi:function-variant" };
// The report page itself: used in the panel (inside .paper) and as the whole document when printed or downloaded.
const REPORT_CSS = `
.paper { background:#fff; color:#222; font:13px/1.45 Arial, Helvetica, sans-serif; padding:28px 32px; border-radius:6px; }
.paper .rhead { border-bottom:3px solid #6d6e71; margin-bottom:18px; padding-bottom:8px; }
.paper h1 { font-size:22px; margin:0; color:#333; } .paper .rsub { color:#6d6e71; font-size:12px; margin-top:4px; }
.paper h2 { font-size:16px; color:#333; margin:22px 0 8px; border-bottom:1px solid #bbb; padding-bottom:3px; text-transform:none; letter-spacing:0; }
.paper h3 { font-size:14px; color:#333; margin:14px 0 6px; text-transform:none; letter-spacing:0; font-weight:700; }
.paper .rsec.two { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
.paper table.rt { width:100%; border-collapse:collapse; font-size:11px; margin:4px 0 8px; }
.paper .rt th, .paper .rt td { border:1px solid #bbb; padding:3px 5px; text-align:left; vertical-align:top; }
.paper .rt th { background:#eee; font-weight:700; } .paper .mono { font-family:Consolas, monospace; white-space:nowrap; }
.paper table.rkv { border-collapse:collapse; font-size:12px; } .paper .rkv th { text-align:left; padding:2px 14px 2px 0; color:#6d6e71; font-weight:400; vertical-align:top; } .paper .rkv td { padding:2px 0; }
.paper .rprods { display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:14px; }
.paper .rprod, .paper .rbutton { border:1px solid #ccc; border-radius:4px; padding:8px 10px; break-inside:avoid; page-break-inside:avoid; }
.paper .rbutton { margin:0 0 10px; } .paper .rbutton h3 { margin:0 0 6px; } .paper .rpos { color:#6d6e71; font-weight:400; font-size:12px; }
.paper .rin { margin:4px 0 4px 6px; } .paper .rin ul { margin:2px 0 0 18px; padding:0; } .paper .rin li { list-style:disc; }
.paper .rout { margin-top:6px; color:#6d6e71; font-size:12px; } .paper .rnote { margin:0 0 6px; color:#444; }
.paper .rblock { break-inside:auto; } .paper .rgroup h2 { margin-top:26px; }
@media print { @page { size:A4; margin:14mm; } body { margin:0; } .paper { padding:0; border-radius:0; } .paper h2 { break-after:avoid; page-break-after:avoid; } }
`;
// editable admin sections: field and input type (dns, users and web access have their own forms)
const ADMIN_FORMS = {
  network: [["ipAddress", "text"], ["netmask", "text"], ["gateway", "text"], ["httpPort", "number"], ["httpsPort", "number"]],
  time: [["synchroniseTimeAgainstServer", "bool"], ["serverName", "text"], ["syncIntervalInHours", "number"], ["gmtOffsetInHours", "number"], ["useDST", "bool"]],
  smtp: [["hostname", "text"], ["hostport", "number"], ["username", "text"], ["password", "password"]],
  email_control: [["emailAddress", "text"], ["serverIPAddress", "text"], ["serverPortNumber", "number"], ["pop3Username", "text"],
    ["pop3Password", "password"], ["pollInterval", "number"], ["removeEmailsAfterUsage", "bool"]],
};
const SECRET_KEYS = new Set(["password", "pop3Password"]);
const ADMIN_LABELS = {
  da: { ipAddress: "IP-adresse", netmask: "Netmaske", gateway: "Gateway", httpPort: "HTTP-port", httpsPort: "HTTPS-port",
    synchroniseTimeAgainstServer: "Synkronisér med tidsserver", serverName: "Tidsserver", syncIntervalInHours: "Synkronisér hver (timer)",
    gmtOffsetInHours: "Tidszone (timer fra UTC)", useDST: "Sommertid", hostname: "SMTP-server", hostport: "Port", username: "Brugernavn",
    password: "Adgangskode", emailAddress: "Controllerens e-mailadresse", serverIPAddress: "POP3-server", serverPortNumber: "Port",
    pop3Username: "POP3-brugernavn", pop3Password: "POP3-adgangskode", pollInterval: "Hent mails hver (min.)",
    removeEmailsAfterUsage: "Slet mails efter brug", enabled: "E-mail-kontrol slået til", primary: "Primær DNS", secondary: "Sekundær DNS",
    firstname: "Fornavn", lastname: "Efternavn", email: "E-mail", phone: "Telefon",
    m_usbLoginRequired_usb: "Kræv login via USB", m_openapi_used: "Åben for tredjepartsprodukter (IHC API)",
    m_administrator: "IHC Administrator", m_treeview: "ServiceView / Home Assistant", m_sceneview: "SceneView", m_websceneview: "Web SceneView",
    m_scenedesign: "SceneDesign", m_ihcvisual: "IHC Visual", m_serverstatus: "Serverstatus", m_onlinedocumentation: "Online dokumentation", m_openapi: "IHC API" },
  en: { ipAddress: "IP address", netmask: "Netmask", gateway: "Gateway", httpPort: "HTTP port", httpsPort: "HTTPS port",
    synchroniseTimeAgainstServer: "Synchronise with time server", serverName: "Time server", syncIntervalInHours: "Synchronise every (hours)",
    gmtOffsetInHours: "Time zone (hours from UTC)", useDST: "Daylight saving", hostname: "SMTP server", hostport: "Port", username: "User name",
    password: "Password", emailAddress: "Controller's e-mail address", serverIPAddress: "POP3 server", serverPortNumber: "Port",
    pop3Username: "POP3 user name", pop3Password: "POP3 password", pollInterval: "Fetch mail every (min)",
    removeEmailsAfterUsage: "Delete mails after use", enabled: "E-mail control on", primary: "Primary DNS", secondary: "Secondary DNS",
    firstname: "First name", lastname: "Last name", email: "E-mail", phone: "Phone",
    m_usbLoginRequired_usb: "Require login over USB", m_openapi_used: "Open for third party products (IHC API)",
    m_administrator: "IHC Administrator", m_treeview: "ServiceView / Home Assistant", m_sceneview: "SceneView", m_websceneview: "Web SceneView",
    m_scenedesign: "SceneDesign", m_ihcvisual: "IHC Visual", m_serverstatus: "Server status", m_onlinedocumentation: "Online documentation", m_openapi: "IHC API" },
};
// values the controller sends as IHC Administrator text keys (from its language files, without the "text." prefix)
const ADMIN_TEXT = {
  da: {
    "usermanager.group_administrators": "Administratorer", "usermanager.group_users": "Brugere",
    "control.email_type": "E-mail", "control.sms_type": "SMS", "notification.email_type": "E-mail", "notification.sms_type": "SMS",
    "control_log.executed_event": "Udført", "control_log.aborted_event": "Afbrudt", "control_log.negotiation_event": "Afventer bekræftelse",
    "control_log.unauthorized_event": "Uautoriseret", "control_log.unknown_event": "Ukendt",
    "emailcontrol.authorization.direct_control": "Direkte styring", "emailcontrol.authorization.sender_based": "Afsenderbaseret",
    "emailcontrol.authorization.three_way": "3-vejs bekræftelse",
    "sms_modem.ok": "OK", "sms_modem.initialising": "Initialiserer", "sms_modem.internal_error": "Intern fejl",
    "sms_modem.unspecific_error": "Ukendt fejl", "sms_modem.gsm_state.no_open_carrier": "Netværk ikke fundet",
    "sms_modem.sim_card.no_card": "Intet SIM-kort", "sms_modem.sim_card.locked_puk": "SIM-kort PUK-låst",
    "sms_modem.sim_card.locked_unknown_pin": "SIM-kort låst", "sms_modem.sim_card.unspecific_error": "SIM-kort – ukendt fejl",
    "sms_modem.antenna_coverage.high": "Høj", "sms_modem.antenna_coverage.medium_high": "Middel-høj",
    "sms_modem.antenna_coverage.medium": "Middel", "sms_modem.antenna_coverage.medium_low": "Middel-lav",
    "sms_modem.antenna_coverage.low": "Lav", "sms_modem.antenna_coverage.not_applicable": "–",
  },
  en: {
    "usermanager.group_administrators": "Administrators", "usermanager.group_users": "Users",
    "control.email_type": "E-mail", "control.sms_type": "SMS", "notification.email_type": "E-mail", "notification.sms_type": "SMS",
    "control_log.executed_event": "Executed", "control_log.aborted_event": "Aborted", "control_log.negotiation_event": "Awaiting confirmation",
    "control_log.unauthorized_event": "Unauthorized", "control_log.unknown_event": "Unknown",
    "emailcontrol.authorization.direct_control": "Direct control", "emailcontrol.authorization.sender_based": "Sender based",
    "emailcontrol.authorization.three_way": "3-way handshake",
    "sms_modem.ok": "OK", "sms_modem.initialising": "Initialising", "sms_modem.internal_error": "Internal error",
    "sms_modem.unspecific_error": "Unknown error", "sms_modem.gsm_state.no_open_carrier": "No network found",
    "sms_modem.sim_card.no_card": "No SIM card", "sms_modem.sim_card.locked_puk": "SIM card PUK locked",
    "sms_modem.sim_card.locked_unknown_pin": "SIM card locked", "sms_modem.sim_card.unspecific_error": "SIM card – unknown error",
    "sms_modem.antenna_coverage.high": "High", "sms_modem.antenna_coverage.medium_high": "Medium high",
    "sms_modem.antenna_coverage.medium": "Medium", "sms_modem.antenna_coverage.medium_low": "Medium low",
    "sms_modem.antenna_coverage.low": "Low", "sms_modem.antenna_coverage.not_applicable": "–",
  },
};

const KIND_ICON = {
  bool: "mdi:toggle-switch-outline", temperature: "mdi:thermometer", time: "mdi:clock-outline",
  timer: "mdi:timer-outline", timertime: "mdi:timer-cog-outline", enum: "mdi:format-list-bulleted-type",
  integer: "mdi:numeric", weekday: "mdi:calendar-week", date: "mdi:calendar", scene: "mdi:palette-outline",
  unknown: "mdi:help-circle-outline",
};
const CAT_ICON = {
  group: "mdi:door-open", product: "mdi:chip", functionblock: "mdi:function-variant",
  section: "mdi:format-list-bulleted", program: "mdi:script-text-outline",
};

// Must equal "version" in manifest.json / VERSION in const.py (a test checks this)
const PANEL_VERSION = "0.12.0";
const POLL_MS = 3000;
const HOLD_INTENT_MS = 150;  // a finger must rest this long on "hold to change" before it counts as a press
const HOLD_MOVE_PX = 8;      // moving more than this before then is a scroll
const HOLD_MAX_MS = 60000;   // a hold never lasts longer
const ADMIN_RECHECK_MS = 15000; // flipping between tabs must not hammer the controller
const MAX_POLL_IDS = 200;

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const humanize = (key) => key.replace(/([a-z0-9])([A-Z])/g, "$1 $2").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

function iconFor(n) {
  if (n.category === "resource") {
    if (/input$/.test(n.tag) && n.kind === "bool") return "mdi:login-variant";
    if (/output$/.test(n.tag) && n.kind === "bool") return "mdi:logout-variant";
    return KIND_ICON[n.kind] || KIND_ICON.unknown;
  }
  return CAT_ICON[n.category] || "mdi:circle-small";
}

class ViewMyIHCPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._started = false;
    this._tab = "project";
    this._view = "all";
    this._controller = null;
    this._controllers = [];
    this._info = null;
    this._state = "idle"; // idle | loading | ready | no_ihc | error
    this._error = "";
    this._kids = new Map();
    this._expanded = new Set();
    this._selected = null;
    this._detail = null;
    this._query = "";
    this._results = null;
    this._values = new Map();
    this._visible = new Set();
    this._admin = null;
    this._adminState = "idle";
    this._adminSavedAt = null;   // when the shown admin data was read from the controller (epoch seconds)
    this._adminChecked = 0;      // last completed refresh (ms)
    this._adminBusy = false;
    this._adminBar = null;
    this._adminBarTimer = null;
    this._adminMarks = new Map();    // section -> Map(JSON path -> change)
    this._adminRemoved = new Map();  // section -> [removed changes]
    this._adminUnits = new Map();    // section -> Set of change units (a whole user counts once)
    this._timer = null;
    this._toast = "";
    this._modal = null;
    this._backendVersion = null;
    this._areas = null;
    this._entityRows = null;  // rows of viewmyihc/entity/list: entities that exist in the ihc integration
    this._entFilter = { q: "", platform: "" };
    this._paintedAt = 0;
    this._existing = new Map(); // ihc id -> entities that already exist in the ihc integration
    this._check = null;       // result of viewmyihc/entity/check
    this._checkBusy = false;
    this._checkError = "";
    this._ctl = null;         // runtime/initial value of the selected resource, typed by the controller
    this._hold = null;        // active hold-to-change { id, keep, started, failed }
  }

  // ------------------------------------------------------------------ HA contract

  set hass(hass) {
    this._hass = hass;
    if (this._started) this._paintStates();
    if (!this._started) {
      this._started = true;
      this._build();
      this._start();
    }
    if (this._menu) this._menu.hass = hass;
  }
  get hass() { return this._hass; }
  set narrow(v) { this._narrow = !!v; if (this._menu) this._menu.narrow = this._narrow; this.classList.toggle("narrow", this._narrow); }
  set panel(_) {}
  set route(_) {}

  connectedCallback() { if (this._started) this._schedule(); }
  disconnectedCallback() { clearTimeout(this._timer); this._timer = null; this._holdEnd(); }

  get _lang() { return (this._hass?.language || "en").startsWith("da") ? "da" : "en"; }
  t(key) { return I18N[this._lang][key] ?? I18N.en[key] ?? key; }
  tk(group, key) { return (I18N[this._lang][group] || {})[key] ?? key; }

  _ws(msg) {
    if (this._controller) msg.controller = this._controller;
    return this._hass.callWS(msg);
  }

  // ------------------------------------------------------------------ lifecycle

  async _start() {
    try {
      const status = await this._hass.callWS({ type: "viewmyihc/status" });
      this._backendVersion = status.version || null;
      this._controllers = status.controllers;
      if (!status.controllers.length) { this._state = "no_ihc"; this._render(); return; }
      this._controller = status.controllers[0].serial;
      this._haUser = status.controllers[0].ha_user || "";
    } catch (err) {
      this._fail(err); return;
    }
    await this._load(false);
  }

  async _load(force) {
    this._state = "loading"; this._render();
    try {
      const res = await this._ws({ type: "viewmyihc/load", force });
      this._controller = res.controller;
      this._info = res.info;
      this._kids.clear(); this._results = null; this._detail = null; this._selected = null;
      await this._restoreExpanded();
      this._state = "ready";
      this._render();
      this._schedule(true);
      this._loadExisting();
    } catch (err) {
      this._fail(err);
    }
  }

  _fail(err) {
    if (err && err.code === "no_ihc") this._state = "no_ihc";
    else { this._state = "error"; this._error = (err && (err.message || err.code)) || String(err); }
    this._render();
  }

  async _loadKids(id) {
    if (this._kids.has(id)) return this._kids.get(id);
    const kids = await this._ws({ type: "viewmyihc/children", parent: id, view: this._view });
    this._kids.set(id, kids);
    return kids;
  }

  // ------------------------------------------------------------------ live values

  _schedule(immediate) {
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this._poll(), immediate ? 250 : POLL_MS);
  }

  async _poll() {
    if (!this.isConnected) return;
    const ids = document.hidden || this._state !== "ready" ? []
      : this._tab === "modules" ? [...new Set([...this._dlIds(), ...(this._selected != null ? [this._selected] : [])])]
      : this._tab === "map" ? this._mapCardIds()
      : this._tab === "project" ? [...new Set([...this._visible, ...(this._selected != null ? [this._selected] : [])])]
          .filter((id) => this._isResource(id)).slice(0, MAX_POLL_IDS)
      : [];
    for (let i = 0; i < ids.length; i += MAX_POLL_IDS) {
      const chunk = ids.slice(i, i + MAX_POLL_IDS);
      try {
        const values = await this._ws({ type: "viewmyihc/values", ids: chunk });
        for (const id of chunk) this._values.set(id, values[String(id)] ?? null);
        this._paintValues();
      } catch (_err) { /* keep old values; the controller may be busy */ }
    }
    this._schedule(false);
  }

  _isResource(id) {
    const n = this._known(id);
    return n && n.category === "resource";
  }

  _known(id) {
    for (const list of this._kids.values()) { const n = list.find((k) => k.id === id); if (n) return n; }
    const hit = (this._results || []).find((k) => k.id === id);
    if (hit) return hit;
    if (this._detail && this._detail.id === id) return { ...this._detail, kind: this._detail.kind };
    return null;
  }

  fmt(kind, v) {
    if (v === null || v === undefined) return { text: "–", cls: "none" };
    switch (kind) {
      case "bool": return v ? { text: this.t("on"), cls: "on" } : { text: this.t("off"), cls: "off" };
      case "temperature": return { text: `${Number(v).toFixed(1)} °C`, cls: "num" };
      case "time": case "timertime": return { text: this._timeText(v), cls: "num" };
      case "timer": return { text: this._timerText(v), cls: "num" };
      case "date": return { text: String(v).slice(0, 10), cls: "num" };
      case "integer": return { text: String(v), cls: "num" };
      default: return { text: String(v), cls: "txt" };
    }
  }
  _timeText(v) {
    if (typeof v === "number") return this._timerText(v);
    const m = String(v).match(/(\d{1,2}):(\d{2})(?::(\d{2}))?/);
    return m ? `${m[1].padStart(2, "0")}:${m[2]}${m[3] ? ":" + m[3] : ""}` : String(v);
  }
  _timerText(ms) {
    ms = Number(ms);
    if (!isFinite(ms)) return String(ms);
    const s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60, rest = ms % 1000;
    const base = h ? `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}` : `${m}:${String(sec).padStart(2, "0")}`;
    return rest ? `${base}.${String(rest).padStart(3, "0")}` : base;
  }

  _paintValues() {
    const root = this.shadowRoot;
    root.querySelectorAll("[data-val]").forEach((el) => {
      const id = Number(el.dataset.val);
      if (!this._values.has(id)) return;
      const { text, cls } = this.fmt(el.dataset.kind, this._values.get(id));
      el.textContent = text;
      el.className = `val ${cls}`;
    });
    root.querySelectorAll("[data-segval]").forEach((el) => {
      const id = Number(el.dataset.segval);
      if (this._values.has(id)) el.classList.toggle("active", String(!!this._values.get(id)) === el.dataset.value);
    });
  }

  // ------------------------------------------------------------------ actions

  async _toggle(id) {
    if (this._expanded.has(id)) this._expanded.delete(id);
    else { this._expanded.add(id); await this._loadKids(id); }
    this._renderTree();
  }

  async _select(id, { reveal = false } = {}) {
    if (this._hold && this._hold.id !== id) this._holdEnd();
    this._selected = id;
    this._detailError = "";
    try { this._detail = await this._ws({ type: "viewmyihc/detail", ihc_id: id }); }
    catch (e) { this._detail = null; this._detailError = (e && (e.message || e.code)) || String(e); }
    if (this._detail?.kind && !this._values.has(id)) this._poll();
    if (this._detail?.kind) this._loadCtl(id);
    this._renderDetail();
    this._renderTree();
    if (reveal) this._scrollToSelected();
    this._markDlSelected();
  }

  // ------------------------------------------------------------------ changing values

  // Runtime + initial value as the controller types them (the type decides which editor is shown).
  async _loadCtl(id) {
    this._ctl = { id, loading: true };
    try {
      const res = await this._ws({ type: "viewmyihc/resource", ihc_id: id });
      if (this._ctl?.id === id) this._ctl = { id, ...res };
    } catch (e) {
      if (this._ctl?.id === id) this._ctl = { id, loadError: this._errText(e) };
    }
    if (this._selected === id) this._renderDetail();
  }

  _errText(e) { return (e && (e.message || e.code)) || String(e); }

  // The value as the live poll reports it (enum: its name), so the tree and the detail stay consistent.
  _pollValue(info) { return info && info.type === "WSEnumValue" ? info.name : info ? info.value : null; }

  _ctlText(info) {
    if (!info) return "–";
    switch (info.type) {
      case "WSBooleanValue": return info.value ? this.t("on") : this.t("off");
      case "WSEnumValue": return info.name ?? String(info.value);
      case "WSTimerValue": return this._timerText(info.value);
      case "WSFloatingPointValue": return info.value == null ? "–" : String(Math.round(info.value * 100) / 100);
      default: return info.value == null ? "–" : String(info.value);
    }
  }

  // Read the editor for `target` ("runtime" / "initial"); undefined when the input is not usable.
  _ctlInput(target, info) {
    const el = this.shadowRoot.querySelector(`[data-ctl="${target}"]`); if (!el) return undefined;
    const raw = el.value.trim();
    switch (info.type) {
      case "WSIntegerValue": return raw === "" ? undefined : Number(raw);
      case "WSFloatingPointValue": return raw === "" ? undefined : Number(raw.replace(",", "."));
      case "WSTimerValue": return raw === "" ? undefined : Math.round(Number(raw.replace(",", ".")) * 1000);
      case "WSTimeValue": return raw.length === 5 ? `${raw}:00` : raw;
      case "WSEnumValue": return Number(raw);
      default: return undefined;
    }
  }

  async _ctlPut(target, value) {
    const c = this._ctl, d = this._detail;
    if (!c || !d || c.id !== d.id) return;
    if (value === undefined || Number.isNaN(value)) { c.error = this.t("badValue"); this._renderDetail(); return; }
    const info = c[target];
    if (target === "initial") {
      const shown = info.type === "WSBooleanValue" ? (value ? this.t("on") : this.t("off"))
        : info.type === "WSEnumValue" ? (d.enum?.values.find((v) => v.id === value)?.name ?? value)
        : info.type === "WSTimerValue" ? this._timerText(value) : value;
      if (!confirm(this.t("confirmInitial").replace("{name}", d.name).replace("{value}", shown))) return;
    }
    c.busy = target; c.error = ""; this._renderDetail();
    try {
      const res = await this._ws({ type: "viewmyihc/set", ihc_id: c.id, value, target });
      Object.assign(c, res);
      this._values.set(c.id, this._pollValue(res.runtime));
      this._showToast(this.t(target === "initial" ? "savedInitial" : "savedValue"));
    } catch (e) { c.error = this._errText(e); }
    c.busy = null;
    if (this._selected === c.id) { this._renderDetail(); this._renderTree(); }
  }

  // Hold-to-change: the backend flips the value and puts it back on release, or by itself when keep-alives stop.
  _holdCancelIntent() {
    if (this._holdIntent) { clearTimeout(this._holdIntent.timer); this._holdIntent = null; }
  }

  _holdStart(id) {
    if (this._hold) return;
    const h = this._hold = { id, keep: null, failed: false };
    h.limit = setTimeout(() => { if (this._hold === h) this._holdEnd(); }, HOLD_MAX_MS);  // never longer than this
    this._paintHold();
    h.started = this._ws({ type: "viewmyihc/hold", ihc_id: id, action: "start" }).then((res) => {
      this._values.set(id, res.value); this._paintValues();
      if (this._hold !== h) return;  // released before the controller answered: _holdEnd releases it
      h.keep = setInterval(() => {
        this._ws({ type: "viewmyihc/hold", ihc_id: id, action: "keep" })
          .then((r) => { if (!r.holding && this._hold === h) this._holdEnd(); }).catch(() => {});
      }, 1000);
    }).catch((e) => {
      h.failed = true;
      if (this._ctl?.id === id) this._ctl.error = this._errText(e);
      if (this._hold === h) this._hold = null;
      this._renderDetail();
    });
  }

  async _holdEnd() {
    const h = this._hold; if (!h) return;
    this._hold = null; clearInterval(h.keep); clearTimeout(h.limit);
    this._paintHold();
    await h.started;
    if (h.failed) return;
    try {
      const res = await this._ws({ type: "viewmyihc/hold", ihc_id: h.id, action: "release" });
      if (res.value !== null && res.value !== undefined) { this._values.set(h.id, res.value); this._paintValues(); }
    } catch (e) {
      if (this._ctl?.id === h.id) { this._ctl.error = this._errText(e); this._renderDetail(); }
    }
  }

  _paintHold() {
    const btn = this.shadowRoot.querySelector("[data-hold]"); if (!btn) return;
    const on = !!this._hold && this._hold.id === Number(btn.dataset.hold);
    btn.classList.toggle("holding", on);
    btn.setAttribute("aria-pressed", String(on));
    btn.querySelector(".htext").textContent = this.t(on ? "holding" : "hold");
  }

  _editor(target, info, d) {
    const busy = this._ctl.busy === target, dis = busy || !!this._hold ? "disabled" : "";
    if (!info) return `<span class="dim">–</span>`;
    if (!info.editable) return `<span class="dim">${esc(this.t("notEditable").replace("{type}", info.type))}</span>`;
    const setBtn = `<button class="btn small" data-act="ctl-set" data-target="${target}" ${dis}>${esc(busy ? this.t("saving") : this.t("set"))}</button>`;
    switch (info.type) {
      case "WSBooleanValue":
        return `<div class="segmented" role="group">${[false, true].map((v) =>
          `<button class="seg ${info.value === v ? "active" : ""}" ${target === "runtime" ? `data-segval="${this._ctl.id}"` : ""} data-act="ctl-bool" data-target="${target}" data-value="${v}" ${dis}>${esc(this.t(v ? "on" : "off"))}</button>`).join("")}</div>`;
      case "WSIntegerValue": case "WSFloatingPointValue": {
        const lim = `${info.min != null ? `min="${info.min}"` : ""} ${info.max != null ? `max="${info.max}"` : ""}`;
        return `<span class="ctl-edit"><input type="number" data-ctl="${target}" value="${esc(info.value ?? "")}" step="${info.type === "WSIntegerValue" ? 1 : "any"}" ${lim} />${setBtn}</span>
          ${info.min != null && info.max != null ? `<small class="dim">${esc(info.min)} – ${esc(info.max)}</small>` : ""}`;
      }
      case "WSTimerValue":
        return `<span class="ctl-edit"><input type="number" data-ctl="${target}" value="${info.value != null ? info.value / 1000 : ""}" step="0.1" min="0" /><span class="dim">${esc(this.t("seconds"))}</span>${setBtn}</span>`;
      case "WSTimeValue":
        return `<span class="ctl-edit"><input type="time" step="1" data-ctl="${target}" value="${esc(info.value ?? "")}" />${setBtn}</span>`;
      case "WSEnumValue": {
        const opts = (d.enum?.values || []).map((v) => `<option value="${v.id}" ${v.id === info.value ? "selected" : ""}>${esc(v.name)}</option>`).join("");
        return opts ? `<span class="ctl-edit"><select data-ctl="${target}">${opts}</select>${setBtn}</span>` : `<span class="dim">${esc(this._ctlText(info))}</span>`;
      }
      default: return "";
    }
  }

  _controlHtml(d) {
    const c = this._ctl && this._ctl.id === d.id ? this._ctl : null;
    const head = `<h3>${esc(this.t("control"))}</h3>`;
    if (!c || c.loading) return `${head}<p class="dim small">${esc(this.t("ctlLoading"))}</p>`;
    if (c.loadError) return `${head}<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(c.loadError)}</p>
      <button class="btn-text small" data-act="ctl-reload">${esc(this.t("retry"))}</button>`;
    const isBool = c.runtime?.type === "WSBooleanValue";
    const holding = !!this._hold && this._hold.id === d.id;
    return `${head}<div class="ctl">
      ${c.error ? `<p class="ferr box">${esc(c.error)}</p>` : ""}
      <div class="ctl-row"><span class="lbl">${esc(this.t("current"))}</span>${this._editor("runtime", c.runtime, d)}</div>
      ${isBool ? `<button class="holdbtn ${holding ? "holding" : ""}" data-hold="${d.id}" aria-pressed="${holding}" ${c.busy ? "disabled" : ""}>
          <ha-icon icon="mdi:gesture-tap-hold"></ha-icon><span class="htext">${esc(this.t(holding ? "holding" : "hold"))}</span></button>
        <p class="help">${esc(this.t("holdHelp"))}</p>` : ""}
      <div class="ctl-row"><span class="lbl">${esc(this.t("ctlInitial"))}</span>${this._editor("initial", c.initial, d)}</div>
      <p class="help">${esc(this.t("ctlInitialHelp"))}</p>
    </div>`;
  }

  async _reveal(id) {
    let detail;
    try { detail = await this._ws({ type: "viewmyihc/detail", ihc_id: id }); } catch (_e) { return; }
    // the target may live in the part of the project the active view hides, so reveal it in "all"
    if (this._view !== "all") { this._view = "all"; this._kids.clear(); this._renderToolbar(); }
    this._query = ""; this._results = null;
    const input = this.shadowRoot.querySelector(".search input"); if (input) input.value = "";
    await this._restoreExpanded();
    for (const p of detail.path.slice(0, -1)) { await this._loadKids(p.id); this._expanded.add(p.id); }
    await this._select(id, { reveal: true });
  }

  _scrollToSelected() {
    const row = this.shadowRoot.querySelector(`.row[data-id="${this._selected}"]`);
    if (row) row.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  // After the children cache was cleared (new view / refresh): reload what is expanded and drop
  // expanded nodes that no longer exist or have nothing to show in the active view.
  async _restoreExpanded() {
    const keep = new Set();
    const queue = [0];
    while (queue.length) {
      const kids = await this._loadKids(queue.shift());
      for (const k of kids) if (this._expanded.has(k.id) && k.has_children) { keep.add(k.id); queue.push(k.id); }
    }
    this._expanded = keep;
  }

  async _setView(view) {
    if (view === this._view) return;
    this._view = view; this._kids.clear(); this._results = null; this._query = "";
    const input = this.shadowRoot.querySelector(".search input"); if (input) input.value = "";
    this._renderToolbar();
    try { await this._restoreExpanded(); } catch (e) { this._fail(e); return; }
    this._renderTree();
  }

  async _doSearch(q) {
    this._query = q;
    if (!q.trim()) { this._results = null; this._renderTree(); return; }
    try {
      const res = await this._ws({ type: "viewmyihc/search", query: q, view: this._view });
      if (q === this._query) { this._results = res; this._renderTree(); }
    } catch (e) { this._fail(e); }
  }

  async _copy(text) {
    try { await navigator.clipboard.writeText(text); }
    catch (_e) {
      const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta);
      ta.select(); try { document.execCommand("copy"); } catch (_e2) { /* ignore */ } ta.remove();
    }
    this._showToast(`${this.t("copied")}: ${text}`);
  }
  _showToast(text) {
    const el = this.shadowRoot.querySelector(".toast"); if (!el) return;
    el.textContent = text; el.classList.add("show");
    clearTimeout(this._toastTimer); this._toastTimer = setTimeout(() => el.classList.remove("show"), 1600);
  }

  // Administration: show the last saved state at once, read the controller in the background, compare, and
  // tell the user what happened. The controller has no "settings changed" marker, so the comparison is ours.
  async _openAdmin(force = false) {
    this._tab = "admin"; this._renderTabs();
    if (!this._admin && this._adminState !== "ready") {
      this._adminState = "loading"; this._renderBody();
      try {
        const snap = await this._ws({ type: "viewmyihc/admin/snapshot" });   // answered by Home Assistant, no controller call
        if (snap.sections) { this._admin = snap.sections; this._adminSavedAt = snap.saved; }
        this._haUser = snap.ha_user || "";
      } catch (_e) { /* nothing saved yet: the skeleton stays until the controller has answered */ }
      this._adminState = this._admin ? "ready" : "loading";
    }
    if (this._tab === "admin") this._renderBody();
    if (force || Date.now() - this._adminChecked > ADMIN_RECHECK_MS) this._refreshAdmin();
    if (force || !this._scene) this._loadScene(!!force);
  }

  async _refreshAdmin() {
    if (this._adminBusy) return;
    this._adminBusy = true;
    const had = !!this._admin;
    this._setAdminBar({
      kind: "info", spin: true,
      text: had ? this.t("adminUpdating").replace("{time}", this._clock(this._adminSavedAt)) : this.t("adminFirstLoad"),
    });
    try {
      const res = await this._ws({ type: "viewmyihc/admin/refresh" });
      const savedBefore = this._adminSavedAt;
      this._admin = res.sections; this._adminSavedAt = res.fetched; this._adminChecked = Date.now(); this._adminState = "ready";
      this._adminMarks = new Map(); this._adminRemoved = new Map(); this._adminUnits = new Map();
      for (const c of res.changes) {
        const unit = c.path[0].startsWith("[") ? `item:${c.path[0]}` : JSON.stringify(c.path);
        if (!this._adminUnits.has(c.section)) this._adminUnits.set(c.section, new Set());
        this._adminUnits.get(c.section).add(unit);
        if (c.type === "removed") { if (!this._adminRemoved.has(c.section)) this._adminRemoved.set(c.section, []); this._adminRemoved.get(c.section).push(c); }
        else { if (!this._adminMarks.has(c.section)) this._adminMarks.set(c.section, new Map()); this._adminMarks.get(c.section).set(JSON.stringify(c.path), c); }
      }
      const units = [...this._adminUnits.values()].reduce((n, set) => n + set.size, 0);
      if (units) {
        this._setAdminBar({ kind: "warn", icon: "mdi:star-four-points", autohide: 12000, text: this.t("adminChanges").replace("{n}", units).replace("{time}", this._clock(savedBefore)) });
      } else if (res.errors.length) {
        this._setAdminBar({ kind: "warn", icon: "mdi:alert-outline", autohide: 10000, text: this.t("adminPartial").replace("{n}", res.errors.length) });
      } else {
        this._setAdminBar({ kind: "ok", icon: "mdi:check-circle-outline", autohide: 3500, text: this.t(res.first ? "adminFetched" : "adminUptodate") });
      }
    } catch (e) {
      if (had) {
        this._setAdminBar({ kind: "error", icon: "mdi:alert-circle-outline", action: "refresh-admin", actionText: this.t("retry"),
          text: this.t("adminFailed").replace("{time}", this._clock(this._adminSavedAt)) });
      } else {
        this._adminState = "error"; this._adminError = (e && (e.message || e.code)) || String(e);
        this._setAdminBar(null);
      }
    } finally { this._adminBusy = false; }
    if (this._tab === "admin") this._renderBody();
  }

  _clock(epoch) {
    if (!epoch) return "–";
    return new Date(epoch * 1000).toLocaleTimeString(this._hass?.language || undefined, { hour: "2-digit", minute: "2-digit" });
  }

  // The status bar at the top of the Administration tab. Messages that need no action remove themselves.
  _setAdminBar(bar) {
    clearTimeout(this._adminBarTimer);
    this._adminBar = bar;
    this._renderAdminBar();
    if (bar && bar.autohide) {
      this._adminBarTimer = setTimeout(() => {
        const el = this.shadowRoot.querySelector(".admin-bar");
        if (el) el.classList.add("leaving");
        setTimeout(() => { if (this._adminBar === bar) { this._adminBar = null; this._renderAdminBar(); } }, 350);
      }, bar.autohide);
    }
  }

  _renderAdminBar() {
    const host = this.shadowRoot.querySelector(".admin-bar-host"); if (!host) return;
    const b = this._adminBar;
    if (!b) { host.innerHTML = ""; return; }
    host.innerHTML = `<div class="admin-bar ${b.kind} ${b.spin ? "spin" : ""}" role="status" aria-live="polite">
      ${b.spin ? `<span class="spinner small"></span>` : `<ha-icon icon="${b.icon || "mdi:information-outline"}"></ha-icon>`}
      <span class="msg">${esc(b.text)}</span>
      ${b.action ? `<button class="btn small" data-act="${b.action}">${esc(b.actionText)}</button>` : ""}
      ${b.kind === "error" || b.kind === "warn" ? `<button class="icon-btn tiny" data-act="dismiss-bar" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button>` : ""}
    </div>`;
  }

  // ------------------------------------------------------------------ rendering

  _build() {
    this.shadowRoot.innerHTML = `
      <style>${this._css()}</style>
      <div class="page">
        <header class="bar">
          <span class="menu"></span>
          <h1></h1>
          <select class="controller" aria-label="Controller" hidden></select>
          <button class="icon-btn refresh" title="" aria-label="refresh"><ha-icon icon="mdi:refresh"></ha-icon></button>
        </header>
        <nav class="tabs" role="tablist"></nav>
        <div class="version-banner" role="alert" hidden></div>
        <main class="body"></main>
        <div class="toast" role="status"></div>
        <div class="modal-host"></div>
      </div>`;
    const menuHost = this.shadowRoot.querySelector(".menu");
    if (customElements.get("ha-menu-button")) {
      this._menu = document.createElement("ha-menu-button");
      this._menu.hass = this._hass; this._menu.narrow = this._narrow;
      menuHost.appendChild(this._menu);
    } else {
      menuHost.innerHTML = `<button class="icon-btn" aria-label="menu"><ha-icon icon="mdi:menu"></ha-icon></button>`;
      menuHost.firstElementChild.addEventListener("click", () =>
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })));
    }
    this.shadowRoot.querySelector(".refresh").addEventListener("click", () => this._refresh());
    this.shadowRoot.querySelector(".controller").addEventListener("change", (e) => {
      this._controller = e.target.value; this._expanded.clear(); this._load(false);
    });
    this.shadowRoot.addEventListener("click", (e) => this._onClick(e));
    this.shadowRoot.addEventListener("keydown", (e) => this._onKey(e));
    for (const ev of ["input", "change"]) this.shadowRoot.addEventListener(ev, (e) => {
      if (e.target.dataset?.af) { this._adminInput(e.target); if (/^password2?$/.test(e.target.dataset.af)) this._pwCheck(); }
      else if (e.target.dataset && "auth" in e.target.dataset && this._adminEdit) this._adminEdit.auth = e.target.value;
    });
    this.shadowRoot.addEventListener("keyup", (e) => {
      if ((e.key === " " || e.key === "Enter") && e.target.closest?.("[data-hold]")) { e.preventDefault(); this._holdEnd(); }
    });
    // Hold-to-change. A mouse holds at once (like the space bar in ServiceView). A finger first has to rest on the
    // button for HOLD_INTENT_MS without moving: otherwise it is a scroll (or a too quick tap) and nothing happens.
    this.shadowRoot.addEventListener("pointerdown", (e) => {
      const btn = e.target.closest?.("[data-hold]"); if (!btn || btn.disabled || e.button !== 0) return;
      const id = Number(btn.dataset.hold);
      if (e.pointerType === "touch" || e.pointerType === "pen") {
        this._holdCancelIntent();
        const intent = { pointerId: e.pointerId, x: e.clientX, y: e.clientY };
        intent.timer = setTimeout(() => { if (this._holdIntent === intent) { this._holdIntent = null; this._holdStart(id); } }, HOLD_INTENT_MS);
        this._holdIntent = intent;
        return;  // no preventDefault: the browser may still turn this into a scroll
      }
      e.preventDefault(); btn.setPointerCapture(e.pointerId); this._holdStart(id);
    });
    this.shadowRoot.addEventListener("pointermove", (e) => {
      const it = this._holdIntent;
      if (it && it.pointerId === e.pointerId && Math.hypot(e.clientX - it.x, e.clientY - it.y) > HOLD_MOVE_PX) this._holdCancelIntent();
    });
    this.shadowRoot.addEventListener("contextmenu", (e) => { if (e.target.closest?.("[data-hold]")) e.preventDefault(); });
    // a release anywhere ends the hold – also when the button was redrawn while it was held
    for (const ev of ["pointerup", "pointercancel", "touchend", "touchcancel", "mouseup"]) {
      window.addEventListener(ev, () => { this._holdCancelIntent(); this._holdEnd(); }, true);
    }
    this.shadowRoot.addEventListener("lostpointercapture", (e) => { if (e.target.closest?.("[data-hold]")) this._holdEnd(); });
    window.addEventListener("blur", () => this._holdEnd());
    document.addEventListener("visibilitychange", () => { if (document.hidden) this._holdEnd(); else this._monitorPoll(); });
    this._io = new IntersectionObserver((entries) => {
      let changed = false;
      for (const en of entries) {
        const id = Number(en.target.dataset.id);
        if (en.isIntersecting) { if (!this._visible.has(id)) { this._visible.add(id); changed = true; } }
        else if (this._visible.delete(id)) changed = true;
      }
      if (changed) this._schedule(true);
    }, { root: null, rootMargin: "100px" });
    this._render();
  }

  _refresh() {
    if (this._tab === "admin") this._openAdmin(true); else this._load(true);
  }

  _renderVersionBanner() {
    const el = this.shadowRoot.querySelector(".version-banner"); if (!el) return;
    const mismatch = this._backendVersion !== PANEL_VERSION && this._state !== "idle" && this._state !== "no_ihc"
      && (this._backendVersion !== null || this._state === "ready" || this._state === "error");
    el.hidden = !mismatch;
    if (!mismatch) return;
    const backend = this._backendVersion || this.t("versionOld");
    el.innerHTML = `<ha-icon icon="mdi:restart-alert"></ha-icon><div><strong>${esc(this.t("versionTitle"))}</strong><p>${esc(this.t("versionText").replace("{panel}", PANEL_VERSION).replace("{backend}", backend))}</p></div>`;
  }

  _render() {
    const root = this.shadowRoot;
    this._renderVersionBanner();
    root.querySelector("h1").textContent = this.t("title");
    root.querySelector(".refresh").title = this.t("refresh");
    const sel = root.querySelector(".controller");
    sel.hidden = this._controllers.length < 2;
    sel.innerHTML = this._controllers.map((c) => `<option value="${esc(c.serial)}" ${c.serial === this._controller ? "selected" : ""}>IHC ${esc(c.serial)}</option>`).join("");
    this._renderTabs();
    this._renderBody();
  }

  _renderTabs() {
    const tabs = this.shadowRoot.querySelector(".tabs");
    const icons = { project: "mdi:file-tree", modules: "mdi:expansion-card-variant", map: "mdi:sitemap-outline", entities: "mdi:shape-plus-outline",
      log: "mdi:text-box-search-outline", versions: "mdi:history", reports: "mdi:file-document-multiple-outline",
      admin: "mdi:account-cog-outline", settings: "mdi:cog-outline" };
    tabs.innerHTML = ["project", "modules", "map", "entities", "log", "versions", "reports", "admin", "settings"].map((k) =>
      `<button role="tab" class="tab ${this._tab === k ? "active" : ""}" aria-selected="${this._tab === k}" data-tab="${k}">
         <ha-icon icon="${icons[k]}"></ha-icon>${esc(this.t(k))}</button>`).join("");
  }

  _renderBody() {
    const body = this.shadowRoot.querySelector(".body");
    if (this._state === "loading" || this._state === "idle") {
      body.innerHTML = `<div class="state"><div class="spinner"></div><p>${esc(this.t("loading"))}</p></div>`; return;
    }
    if (this._state === "no_ihc") {
      body.innerHTML = `<div class="state card"><ha-icon icon="mdi:link-off"></ha-icon><h2>${esc(this.t("noIhcTitle"))}</h2><p>${esc(this.t("noIhcText"))}</p></div>`; return;
    }
    if (this._state === "error") {
      body.innerHTML = `<div class="state card err"><ha-icon icon="mdi:alert-circle-outline"></ha-icon><h2>${esc(this.t("errorTitle"))}</h2><p>${esc(this._error)}</p><button class="btn" data-act="retry">${esc(this.t("retry"))}</button></div>`; return;
    }
    if (this._tab === "admin") { this._renderAdmin(body); return; }
    if (this._tab === "modules") { this._renderModules(body); return; }
    if (this._tab === "log") { this._renderLog(body); return; }
    if (this._tab === "versions") { this._renderVersions(body); return; }
    if (this._tab === "settings") { this._renderSettings(body); return; }
    if (this._tab === "reports") { this._renderReports(body); return; }
    if (this._tab === "map") { this._renderMap(body); return; }
    if (this._tab === "entities") { this._renderEntities(body); return; }
    body.innerHTML = `
      <div class="project">
        <section class="panel tree-panel">
          <div class="toolbar"></div>
          <div class="info"></div>
          <div class="tree" role="tree"></div>
        </section>
        <aside class="panel detail-panel"></aside>
      </div>`;
    this._renderToolbar(); this._renderInfo(); this._renderTree(); this._renderDetail();
  }

  _renderToolbar() {
    const el = this.shadowRoot.querySelector(".toolbar"); if (!el) return;
    const seg = ["all", "installation", "programs"].map((v) =>
      `<button class="seg ${this._view === v ? "active" : ""}" data-view="${v}">${esc(this.t(v))}</button>`).join("");
    el.innerHTML = `<div class="segmented" role="group">${seg}</div>
      <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input type="search" placeholder="${esc(this.t("search"))}" value="${esc(this._query)}" /></label>`;
    el.querySelector("input").addEventListener("input", (e) => {
      clearTimeout(this._searchTimer); const v = e.target.value;
      this._searchTimer = setTimeout(() => this._doSearch(v), 250);
    });
  }

  _renderInfo() {
    const el = this.shadowRoot.querySelector(".info"); if (!el || !this._info) return;
    const i = this._info;
    el.innerHTML = `<span>${esc(i.description || "")}</span>
      <span class="dot"></span><span>${i.resources} ${esc(this.t("resources"))}</span>
      <span class="dot"></span><span>${i.functionblocks} ${esc(this.t("blocks"))}</span>
      <span class="dot"></span><span>${i.products} ${esc(this.t("products"))}</span>
      ${i.modified ? `<span class="dot"></span><span>${esc(this.t("modified"))} ${esc(i.modified)}</span>` : ""}`;
  }

  _rows() {
    const rows = [];
    const walk = (parentId, depth) => {
      for (const n of this._kids.get(parentId) || []) {
        rows.push({ n, depth });
        if (n.has_children && this._expanded.has(n.id)) walk(n.id, depth + 1);
      }
    };
    walk(0, 0);
    return rows;
  }

  _rowHtml(n, depth, label) {
    const open = this._expanded.has(n.id);
    const isRes = n.category === "resource";
    const val = isRes ? this._values.get(n.id) : undefined;
    const f = isRes && this._values.has(n.id) ? this.fmt(n.kind, val) : { text: "", cls: "none" };
    return `<div class="row ${this._selected === n.id ? "selected" : ""} cat-${n.category}" role="treeitem" tabindex="0"
        data-id="${n.id}" data-has="${n.has_children ? 1 : 0}" ${n.has_children ? `aria-expanded="${open}"` : ""}
        style="--depth:${depth}">
      <span class="chev ${n.has_children ? "" : "leaf"}">${n.has_children ? `<ha-icon icon="${open ? "mdi:chevron-down" : "mdi:chevron-right"}"></ha-icon>` : ""}</span>
      <ha-icon class="ico ${isRes ? "res" : ""}" icon="${iconFor(n)}"></ha-icon>
      <span class="name">${esc(n.name)}${label ? `<small>${esc(label)}</small>` : n.hint ? `<small>${esc(n.hint)}</small>` : ""}</span>
      ${n.links ? `<span class="chip link" title="${esc(this.t("links"))}"><ha-icon icon="mdi:link-variant"></ha-icon>${n.links}</span>` : ""}
      ${isRes && this._existing.has(n.id) ? `<span class="chip ha" title="${esc(this._existingTitle(n.id))}"><ha-icon icon="mdi:home-assistant"></ha-icon>${this._existing.get(n.id).length > 1 ? this._existing.get(n.id).length : ""}</span>` : ""}
      ${isRes ? `<span class="val ${f.cls}" data-val="${n.id}" data-kind="${esc(n.kind)}">${esc(f.text)}</span>
        <button class="chip id" data-copy="${n.id}" title="${esc(this.t("copy"))}">${n.id}</button>
        <button class="row-act" data-act="create-entity" data-id="${n.id}" title="${esc(this.t("createEntity"))}" aria-label="${esc(this.t("createEntity"))}"><ha-icon icon="mdi:plus-circle-outline"></ha-icon></button>` : ""}
    </div>`;
  }

  _renderTree() {
    const tree = this.shadowRoot.querySelector(".tree"); if (!tree) return;
    let html;
    if (this._results) {
      html = this._results.length
        ? this._results.map((r) => this._rowHtml(r, 0, r.label)).join("")
        : `<p class="no-results">${esc(this.t("noResults"))}</p>`;
    } else {
      html = this._rows().map(({ n, depth }) => this._rowHtml(n, depth)).join("");
    }
    tree.innerHTML = html;
    this._visible.clear();
    tree.querySelectorAll(".row").forEach((r) => this._io.observe(r));
    this._paintValues();
  }

  _renderDetail() {
    const el = this.shadowRoot.querySelector(".detail-panel"); if (!el) return;
    const d = this._detail;
    el.classList.toggle("open", !!d);
    if (!d && this._detailError) {
      el.innerHTML = `<div class="placeholder"><h3>${esc(this.t("errorTitle"))}</h3><p>${esc(this._detailError)}</p></div>`;
      return;
    }
    if (!d && this._tab === "modules") {
      el.innerHTML = `<div class="placeholder"><h3>${esc(this.t("dlPickTitle"))}</h3><p>${esc(this.t("dlPick"))}</p></div>`;
      return;
    }
    if (!d) {
      const steps = this._lang === "da"
        ? ["Fold en lokalitet ud og vælg et produkt eller en funktionsblok.", "Klik på en ressource (række med et ID-tal) for at se detaljer og forbindelser.", "Tryk <b>Opret entitet</b> – eller på <b>+</b> i rækken – for at oprette den i Home Assistant."]
        : ["Expand a location and pick a product or function block.", "Click a resource (a row with an ID number) to see details and connections.", "Press <b>Create entity</b> – or the <b>+</b> in the row – to create it in Home Assistant."];
      el.innerHTML = `<div class="placeholder"><h3>${esc(this.t("noSelection"))}</h3><ol>${steps.map((x) => `<li>${x}</li>`).join("")}</ol></div>`;
      return;
    }
    const isRes = !!d.kind;
    const f = isRes && this._values.has(d.id) ? this.fmt(d.kind, this._values.get(d.id)) : null;
    const attrs = Object.entries(d.attrs || {});
    el.innerHTML = `
      <div class="d-head">
        <button class="icon-btn d-close" data-act="close" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button>
        <div class="d-type"><ha-icon icon="${iconFor({ category: d.category, kind: d.kind, tag: d.tag })}"></ha-icon>
          ${esc(isRes ? this.tk("kind", d.kind) : this.tk("cat", d.category))}</div>
        <h2>${esc(d.name)}</h2>
        ${this._tab !== "project" ? `<button class="btn-text small" data-jump="${d.id}"><ha-icon icon="mdi:file-tree"></ha-icon>${esc(this.t("showInTree"))}</button>` : ""}
        ${d.path.length > 1 ? `<div class="crumbs">${d.path.slice(0, -1).map((p) => `<span>${esc(p.name)}</span>`).join('<ha-icon icon="mdi:chevron-right"></ha-icon>')}</div>` : ""}
      </div>
      ${isRes ? `<div class="idbox">
          <div><span class="lbl">${esc(this.t("id"))}</span><button class="bigid" data-copy="${d.id}" title="${esc(this.t("copy"))}">${d.id}<ha-icon icon="mdi:content-copy"></ha-icon></button></div>
          <div><span class="lbl">${esc(this.t("hex"))}</span><code>${esc(d.id_hex)}</code></div>
          <div class="cur"><span class="lbl">${esc(this.t("current"))}</span>
            <span class="val ${f ? f.cls : "none"}" data-val="${d.id}" data-kind="${esc(d.kind)}">${esc(f ? f.text : "–")}</span></div>
        </div>` : `<div class="idbox"><div><span class="lbl">${esc(this.t("id"))}</span><code>${d.id}</code> <code class="dim">${esc(d.id_hex)}</code></div></div>`}
      ${isRes ? this._controlHtml(d) : ""}
      ${isRes ? this._existingBox(d.id) : ""}
      ${isRes ? this._pressHtml(d) : ""}
      ${isRes ? `<button class="btn wide" data-act="create-entity" data-id="${d.id}"><ha-icon icon="mdi:plus-circle-outline"></ha-icon>${esc(this.t("createEntity"))}</button>` : ""}
      ${d.note ? `<h3>${esc(this.t("note"))}</h3><p class="note">${esc(d.note)}</p>` : ""}
      ${attrs.length ? `<h3>${esc(this.t("values"))}</h3><dl>${attrs.map(([k, v]) => `<dt>${esc(k === "inivalue" ? this.t("iniProject") : humanize(k))}</dt><dd>${esc(v)}</dd>`).join("")}</dl>` : ""}
      ${d.enum ? `<h3>${esc(d.enum.name)}</h3><ul class="enum">${d.enum.values.map((v) => `<li><code>${v.index}</code> ${esc(v.name)}</li>`).join("")}</ul>` : ""}
      ${d.links.length ? `<h3>${esc(this.t("links"))}</h3><ul class="links">${d.links.map((l) => `
        <li><${l.hidden ? `div class="link-item internal" title="${esc(this.t("internalLink"))}"` : `button class="link-item" data-jump="${l.id}"`}>
          <ha-icon icon="${l.direction === "scene" ? "mdi:palette-outline" : l.direction === "to" ? "mdi:arrow-right-bold" : "mdi:arrow-left-bold"}"></ha-icon>
          <span>${esc(l.label)}</span>${l.kind ? `<code>${l.id}</code>` : ""}</${l.hidden ? "div" : "button"}></li>`).join("")}</ul>` : ""}`;
    el.querySelector("details.press")?.addEventListener("toggle", (ev) => { if (this._press) this._press.open = ev.target.open; });
    this._paintValues();
  }

  _renderAdmin(body) {
    if (this._adminState === "error") {
      body.innerHTML = `<div class="state card err"><h2>${esc(this.t("errorTitle"))}</h2><p>${esc(this._adminError)}</p><button class="btn" data-act="refresh-admin">${esc(this.t("retry"))}</button></div>`;
      return;
    }
    const marksTotal = [...this._adminUnits.values()].reduce((n, set) => n + set.size, 0);
    let cards;
    if (!this._admin) {  // nothing saved yet and the controller has not answered: placeholders, not a spinner
      cards = Array.from({ length: 6 }, () => `<section class="card acard skeleton"><i class="sk t"></i><i class="sk"></i><i class="sk"></i><i class="sk s"></i></section>`).join("");
    } else {
      cards = this._admin.map((s) => this._adminCard(s)).join("");
    }
    body.innerHTML = `<div class="admin">
      <div class="admin-bar-host"></div>
      <div class="banner"><ha-icon icon="mdi:lock-outline"></ha-icon><span class="grow">${esc(this.t("readOnly"))}</span>
        ${this._adminSavedAt ? `<span class="fetched">${esc(this.t("updatedAt").replace("{time}", this._clock(this._adminSavedAt)))}</span>` : ""}
        ${marksTotal ? `<button class="btn-text small" data-act="clear-marks">${esc(this.t("clearMarks"))}</button>` : ""}
        <button class="btn small" data-act="refresh-admin" ${this._adminBusy ? "disabled" : ""}>${esc(this.t("refreshAdmin"))}</button></div>
      <div class="cards">${cards}</div>
      <div class="admin-scene">${this._sceneHtml()}</div></div>`;
    this._renderAdminBar();
    this._pwCheck();
  }

  // ------------------------------------------------------------------ changing admin settings
  // The backend reads the controller's own record, replaces only the fields sent and sends the rest back unchanged.

  _adminEditable(key) { return key in ADMIN_FORMS || key === "dns" || key === "users" || key === "web_access"; }

  _adminLabel(key) { return (ADMIN_LABELS[this._lang] || ADMIN_LABELS.en)[key] || humanize(key.replace(/^m_/, "")); }

  _adminStart(key) {
    const s = (this._admin || []).find((x) => x.key === key); if (!s || !("data" in s)) return;
    const data = s.data || {};
    let values = {};
    if (key === "dns") {
      const list = Array.isArray(data) ? data : data ? [data] : [];
      values = { primary: list[0] ? this._adminValue("ipAddress", list[0].ipAddress) : "", secondary: list[1] ? this._adminValue("ipAddress", list[1].ipAddress) : "" };
    } else if (key !== "users") {
      for (const [k, v] of Object.entries(data)) if (typeof v !== "object" || v === null) values[k] = SECRET_KEYS.has(k) ? "" : v ?? "";
    }
    this._adminEdit = { key, values, original: { ...values }, error: "", busy: false, confirm: false, needConfirm: false, user: null };
    this._renderBody();
  }

  _adminCancel() { this._adminEdit = null; this._renderBody(); }

  _adminInput(el) {
    const e = this._adminEdit; if (!e) return;
    const target = e.user ? e.user.values : e.values;
    target[el.dataset.af] = el.type === "checkbox" ? (el.checked ? "true" : "false") : el.value;
  }

  // The password the ihc integration logs in with: asked for every change, never kept.
  _authField() {
    return `<label class="field auth"><span class="lbl2"><ha-icon icon="mdi:shield-key-outline"></ha-icon>${esc(this.t("adminAuth").replace("{user}", this._haUser || "ihc"))}</span>
      <input type="password" autocomplete="current-password" data-auth value="${esc(this._adminEdit?.auth || "")}" /></label>`;
  }

  async _adminSend(msg, after) {
    const e = this._adminEdit; if (!e) return;
    if (!e.auth) { e.error = this.t("adminAuthMissing"); this._renderBody(); this.shadowRoot.querySelector("[data-auth]")?.focus(); return; }
    msg = { ...msg, auth: e.auth };
    e.auth = "";
    e.busy = true; e.error = ""; this._renderBody();
    try {
      const res = await this._ws(msg);
      for (const fresh of res.sections) {
        const i = this._admin.findIndex((x) => x.key === fresh.key);
        if (i >= 0) this._admin[i] = fresh; else this._admin.push(fresh);
        this._adminMarks.delete(fresh.key); this._adminUnits.delete(fresh.key); this._adminRemoved.delete(fresh.key);
      }
      this._showToast(this.t("adminSaved"));
      if (after) after(); else this._adminEdit = null;
    } catch (err) {
      if (err && err.code === "needs_confirm") { e.needConfirm = true; e.error = this.t("adminNeedsConfirm"); }
      else if (err && err.code === "wrong_password") e.error = /many/i.test(err.message || "") ? this.t("adminAuthLocked") : this.t("adminAuthWrong");
      else e.error = this._errText(err);
    }
    if (this._adminEdit) this._adminEdit.busy = false;
    this._renderBody();
  }

  _adminSave() {
    const e = this._adminEdit; if (!e) return;
    if (e.key === "dns") { this._adminSend({ type: "viewmyihc/admin/dns", primary: e.values.primary || "", secondary: e.values.secondary || "" }); return; }
    const changes = {};
    for (const [k, v] of Object.entries(e.values)) {
      if (k === "enabled") continue;
      if (SECRET_KEYS.has(k)) { if (v) changes[k] = v; continue; }
      if (String(v) !== String(e.original[k])) changes[k] = v;
    }
    const enabled = e.key === "email_control" && e.values.enabled !== e.original.enabled;
    if (!Object.keys(changes).length && !enabled) { this._adminCancel(); return; }
    const write = () => this._adminSend({ type: "viewmyihc/admin/write", section: e.key, changes, confirm: e.confirm });
    if (enabled) {
      this._adminSend({ type: "viewmyihc/admin/email_control_enabled", enabled: e.values.enabled === "true" },
        Object.keys(changes).length ? () => { e.original.enabled = e.values.enabled; setTimeout(write); } : null);
    } else write();
  }

  _adminSetClock() {
    if (!confirm(this.t("adminClockConfirm"))) return;
    this._adminSend({ type: "viewmyihc/admin/write", section: "time", changes: {}, set_clock: true }, () => {});
  }

  _field(key, type, value, extra = "") {
    const label = esc(this._adminLabel(key));
    if (type === "bool") return `<label class="switchrow"><input type="checkbox" data-af="${key}" ${String(value) === "true" ? "checked" : ""} ${extra}/><span>${label}</span></label>`;
    const input = type === "password"
      ? `<input type="password" autocomplete="new-password" data-af="${key}" value="${esc(value)}" ${/placeholder=/.test(extra) ? "" : `placeholder="${esc(this.t("adminKeepPassword"))}"`} ${extra}/>`
      : `<input type="${type === "number" ? "number" : "text"}" data-af="${key}" value="${esc(value ?? "")}" ${extra}/>`;
    return `<label class="field"><span class="lbl2">${label}</span>${input}</label>`;
  }

  _adminFooter(e, extra = "") {
    return `${e.error ? `<p class="ferr box">${esc(e.error)}</p>` : ""}
      ${e.needConfirm ? `<label class="switchrow danger"><input type="checkbox" data-act="admin-confirm" ${e.confirm ? "checked" : ""}/><span>${esc(this.t("adminConfirmBox"))}</span></label>` : ""}
      ${this._authField()}
      <div class="formfoot">${extra}<span class="grow"></span>
        <button class="btn-text" data-act="admin-cancel" ${e.busy ? "disabled" : ""}>${esc(this.t("cancel"))}</button>
        <button class="btn small" data-act="admin-save" ${e.busy || (e.needConfirm && !e.confirm) ? "disabled" : ""}>${esc(e.busy ? this.t("saving") : this.t("save"))}</button></div>`;
  }

  _adminForm(s) {
    const e = this._adminEdit, v = e.values;
    const warn = (key) => `<div class="callout"><ha-icon icon="mdi:alert-outline"></ha-icon><div>${esc(this.t(key))}</div></div>`;
    if (s.key === "users") return this._usersForm(s);
    if (s.key === "dns") {
      return `<div class="aform">${this._field("primary", "text", v.primary)}${this._field("secondary", "text", v.secondary)}${this._adminFooter(e)}</div>`;
    }
    if (s.key === "web_access") {
      const programs = ["administrator", "treeview", "sceneview", "websceneview", "scenedesign", "ihcvisual", "serverstatus", "onlinedocumentation", "openapi"];
      const locked = new Set(["m_treeview_internal", "m_administrator_internal"]);
      const cell = (name) => name in v
        ? `<td><input type="checkbox" data-af="${name}" ${String(v[name]) === "true" ? "checked" : ""} ${locked.has(name) ? `disabled title="${esc(this.t("adminLocked"))}"` : ""}/></td>` : "<td>–</td>";
      return `<div class="aform">${warn("adminWebWarn")}
        <div class="tablewrap"><table class="tbl access"><thead><tr><th></th><th>USB</th><th>${esc(this.t("adminLan"))}</th><th>${esc(this.t("adminWan"))}</th></tr></thead><tbody>
          ${programs.map((p) => `<tr><td>${esc(this._adminLabel("m_" + p))}</td>${["usb", "internal", "external"].map((w) => cell(`m_${p}_${w}`)).join("")}</tr>`).join("")}
        </tbody></table></div>
        ${"m_usbLoginRequired_usb" in v ? this._field("m_usbLoginRequired_usb", "bool", v.m_usbLoginRequired_usb) : ""}
        ${"m_openapi_used" in v ? this._field("m_openapi_used", "bool", v.m_openapi_used) : ""}
        ${this._adminFooter(e)}</div>`;
    }
    const fields = ADMIN_FORMS[s.key].filter(([key]) => key in v || SECRET_KEYS.has(key));
    return `<div class="aform">
      ${s.key === "network" ? warn("adminNetWarn") : ""}
      ${s.key === "email_control" && "enabled" in v ? this._field("enabled", "bool", v.enabled) : ""}
      ${fields.map(([key, type]) => this._field(key, type, v[key] ?? "")).join("")}
      ${this._adminFooter(e, s.key === "time" ? `<button class="btn-text" data-act="admin-clock" ${e.busy ? "disabled" : ""}><ha-icon icon="mdi:clock-sync-outline"></ha-icon>${esc(this.t("adminSetClock"))}</button>` : "")}</div>`;
  }

  _usersForm(s) {
    const e = this._adminEdit, list = Array.isArray(s.data) ? s.data : s.data ? [s.data] : [];
    if (e.user) {
      const u = e.user, isNew = u.isNew, isHa = !isNew && u.username === this._haUser;
      return `<div class="aform"><h4 class="tight">${esc(isNew ? this.t("adminNewUser") : u.username)}</h4>
        ${isNew ? this._field("username", "text", u.values.username ?? "") : ""}
        ${this._field("password", "password", u.values.password ?? "", isHa ? `disabled title="${esc(this.t("adminHaUserPw"))}"` : isNew ? 'placeholder=""' : "")}
        <div class="pw-repeat" ${u.values.password ? "" : "hidden"}>
          <label class="field"><span class="lbl2">${esc(this.t("pwRepeat"))}</span>
            <input type="password" autocomplete="new-password" data-af="password2" value="${esc(u.values.password2 ?? "")}" /></label>
          <div class="pw-msg"></div></div>
        ${isNew ? "" : `<p class="help">${esc(this.t(isHa ? "adminHaUserPw" : "adminPasswordHelp"))}</p>`}
        ${["firstname", "lastname", "email", "phone"].map((k) => this._field(k, "text", u.values[k] ?? "")).join("")}
        ${e.error ? `<p class="ferr box">${esc(e.error)}</p>` : ""}
        ${this._authField()}
        <div class="formfoot"><span class="grow"></span><button class="btn-text" data-act="user-back" ${e.busy ? "disabled" : ""}>${esc(this.t("back"))}</button>
          <button class="btn small" data-act="user-save" ${e.busy ? "disabled" : ""}>${esc(e.busy ? this.t("saving") : this.t("save"))}</button></div></div>`;
    }
    return `<div class="aform">${list.map((u) => {
      const isHa = u.username === this._haUser;
      return `<div class="erow"><ha-icon class="eico" icon="${isHa ? "mdi:home-assistant" : "mdi:account-outline"}"></ha-icon>
        <div class="einfo"><div class="ename">${esc(u.username)}</div><div class="esub">${esc([u.firstname, u.lastname].filter(Boolean).join(" "))}${isHa ? ` · ${esc(this.t("adminHaUser"))}` : ""}</div></div>
        <button class="icon-btn" data-act="user-edit" data-user="${esc(u.username)}" title="${esc(this.t("edit"))}"><ha-icon icon="mdi:pencil-outline"></ha-icon></button>
        <button class="icon-btn danger" data-act="user-delete" data-user="${esc(u.username)}" ${isHa || list.length < 2 ? `disabled title="${esc(this.t("adminHaUser"))}"` : `title="${esc(this.t("remove"))}"`}><ha-icon icon="mdi:delete-outline"></ha-icon></button></div>`;
    }).join("")}
      ${e.error ? `<p class="ferr box">${esc(e.error)}</p>` : ""}
      <p class="help">${esc(this.t("adminAuthDelete"))}</p>${this._authField()}
      <div class="formfoot"><button class="btn-text" data-act="user-new"><ha-icon icon="mdi:account-plus-outline"></ha-icon>${esc(this.t("adminNewUser"))}</button><span class="grow"></span>
        <button class="btn small" data-act="admin-cancel">${esc(this.t("close"))}</button></div></div>`;
  }

  _userOpen(username) {
    const e = this._adminEdit; if (!e) return;
    const s = this._admin.find((x) => x.key === "users");
    const list = Array.isArray(s?.data) ? s.data : s?.data ? [s.data] : [];
    const u = username ? list.find((x) => x.username === username) : null;
    const values = { password: "", password2: "" };
    for (const k of ["firstname", "lastname", "email", "phone"]) values[k] = u?.[k] ?? "";
    e.user = { isNew: !u, username: u?.username || "", values, original: { ...values } };
    e.error = ""; this._renderBody();
  }

  // The repeat field appears once something is typed as password; saving waits until both are the same.
  _pwCheck() {
    const u = this._adminEdit?.user; if (!u) return;
    const root = this.shadowRoot, box = root.querySelector(".pw-repeat"); if (!box) return;
    const pw = u.values.password || "";
    if (!pw) { u.values.password2 = ""; const repeat = box.querySelector("input"); if (repeat) repeat.value = ""; }
    box.hidden = !pw;
    const pw2 = u.values.password2 || "";
    const msg = box.querySelector(".pw-msg");
    const state = !pw ? "" : !pw2 ? "" : pw === pw2 ? "ok" : "bad";
    msg.className = `pw-msg ${state}`;
    msg.textContent = state === "ok" ? this.t("pwMatch") : state === "bad" ? this.t("pwMismatch") : "";
    const save = root.querySelector('[data-act="user-save"]');
    if (save && !this._adminEdit.busy) save.disabled = !!pw && pw !== pw2;
  }

  _userSave() {
    const e = this._adminEdit, u = e?.user; if (!u) return;
    if ((u.values.password || "") !== (u.values.password2 || "") && u.values.password) {
      e.error = this.t("pwMismatch"); this._renderBody(); return;
    }
    const details = {};
    for (const k of ["firstname", "lastname", "email", "phone"]) if (u.isNew || u.values[k] !== u.original[k]) details[k] = u.values[k] || "";
    const msg = u.isNew
      ? { type: "viewmyihc/admin/user", action: "add", username: (u.values.username || "").trim(), password: u.values.password || "", details }
      : { type: "viewmyihc/admin/user", action: "update", username: u.username, password: u.values.password || "", details };
    this._adminSend(msg, () => { e.user = null; });
  }

  _userDelete(username) {
    if (!confirm(this.t("adminDeleteUser").replace("{user}", username))) return;
    this._adminSend({ type: "viewmyihc/admin/user", action: "remove", username }, () => { this._adminEdit.user = null; });
  }

  _adminCard(s) {
    const marks = this._adminMarks.get(s.key);
    const removed = this._adminRemoved.get(s.key) || [];
    const n = this._adminUnits.get(s.key)?.size || 0;
    const label = (path) => path.map((seg) => (seg.startsWith("[") ? seg.slice(1, -1) : humanize(seg))).join(" › ");
    // a removed list item (e.g. a user) arrives as one change per field: show it once, by name
    const removedLabels = [...new Map(removed.map((c) => [c.path[0].startsWith("[") ? c.path[0] : JSON.stringify(c.path), c])).values()]
      .map((c) => ({ text: c.path[0].startsWith("[") ? c.path[0].slice(1, -1) : label(c.path), old: c.path[0].startsWith("[") ? null : c.old, item: c.path[0].startsWith("[") }));
    let content;
    const editing = this._adminEdit && this._adminEdit.key === s.key;
    if (editing) content = this._adminForm(s);
    else if (!("data" in s)) content = `<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(this.t("adminError"))}: ${esc(s.error)}</p>`;
    else content = `${s.stale ? `<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(this.t("adminStale"))}: ${esc(s.error)}</p>` : ""}<div class="kv">${s.key === "uptime" ? esc(this._uptime(s.data)) : this._kv(s.data, 0, [], marks)}</div>`;
    return `<section class="card acard ${n ? "changed" : ""} ${editing ? "editing" : ""}">
      <h3>${esc((I18N[this._lang].adminTitle || {})[s.key] || s.title)}${n ? `<span class="chip chg"><span class="star">★</span>${esc(this.t("changedChip").replace("{n}", n))}</span>` : ""}
        ${this._adminEditable(s.key) && "data" in s && !editing && !this._adminEdit ? `<button class="btn-text small right" data-act="admin-edit" data-key="${s.key}"><ha-icon icon="mdi:pencil-outline"></ha-icon>${esc(this.t(s.key === "users" ? "adminManage" : "edit"))}</button>` : ""}</h3>
      ${content}
      ${removed.length ? `<div class="removed"><strong>${esc(this.t("removedItems"))}:</strong> ${removedLabels.map((c) => `<span class="rm" ${c.item ? "" : `title="${esc(this.t("wasValue").replace("{old}", c.old ?? "–"))}"`}>${esc(c.text)}</span>`).join("")}</div>` : ""}
    </section>`;
  }

  // `path` addresses the value exactly like admin_diff.py does (dict keys; "[username]" or "[index]" for lists),
  // so values the backend reported as changed can be marked here.
  _kv(v, depth = 0, path = [], marks = null) {
    const mark = (p, shown) => {
      const c = marks && marks.get(JSON.stringify(p));
      if (!c) return shown;
      const hint = c.type === "added" ? this.t("newValue") : this.t("wasValue").replace("{old}", this._adminValue(p[p.length - 1], c.old) ?? "–");
      return `<span class="chgv" title="${esc(hint)}"><span class="star">★</span>${shown}</span>`;
    };
    const shownValue = (val) => esc(val === null ? "–" : val === "true" ? "✓" : val === "false" ? "✗" : val);
    if (v === null || v === undefined || v === "") return `<span class="dim">${esc(this.t("empty"))}</span>`;
    if (Array.isArray(v)) {
      return v.map((item, i) => {
        const id = item && typeof item === "object" && item.username ? String(item.username) : String(i);
        const p = [...path, `[${id}]`];
        // a whole new list item (a new user): its username was added and everything under it is an addition
        const under = marks ? [...marks.values()].filter((c) => c.path.length > p.length && p.every((seg, k) => c.path[k] === seg)) : [];
        const isNew = under.length > 0 && under.every((c) => c.type === "added")
          && under.some((c) => c.path.length === p.length + 1 && c.path[p.length] === "username");
        return (typeof item === "object" && item !== null)
          ? `<div class="item ${isNew ? "new" : ""}">${isNew ? `<span class="chip chg newbadge"><span class="star">★</span>${esc(this.t("newValue"))}</span>` : ""}${this._kv(item, depth + 1, p, isNew ? null : marks)}</div>`
          : `<div>${mark(p, esc(item))}</div>`;
      }).join("");
    }
    const when = this._wsDate(v);
    if (when) return esc(when);
    if (typeof v === "object") {
      return Object.entries(v).map(([k, val]) => {
        const p = [...path, k];
        const complex = typeof val === "object" && val !== null && !this._wsDate(val);
        const changed = !complex && marks && marks.has(JSON.stringify(p));
        return `<div class="kvrow ${complex ? "complex" : ""} ${changed ? "chg" : ""}"><span class="k">${esc(this._adminLabel(k))}</span><span class="v">${complex ? this._kv(val, depth + 1, p, marks) : mark(p, shownValue(this._adminValue(k, val)))}</span></div>`;
      }).join("");
    }
    return esc(v);
  }

  // How one admin value is shown: clock structures, uptime, IP addresses sent as integers and the Administrator's text keys.
  _adminValue(key, v) {
    const when = this._wsDate(v);
    if (when) return when;
    if (key === "uptime") return this._uptime(v);
    if (typeof v !== "string") return v;
    if (/^text\.[\w.]+$/.test(v)) return this._adminText(v);
    // the controller sends IPv4 addresses as a signed 32-bit integer (134744072 = 8.8.8.8)
    if (/ipaddress|^ip$|mask|gateway|dns/i.test(key) && /^-?\d+$/.test(v) && Math.abs(Number(v)) <= 4294967295) {
      const n = Number(v) >>> 0;
      return [n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join(".");
    }
    return v;
  }

  // Text keys from IHC Administrator's own language files; unknown keys get a readable form of their last part.
  _adminText(key) {
    const known = (ADMIN_TEXT[this._lang] || ADMIN_TEXT.en)[key.slice(5)];
    if (known) return known;
    const tail = key.split(".").pop();
    if (/(^|_)sms(_|$)/i.test(tail)) return "SMS";
    if (/(^|_)e_?mail(_|$)/i.test(tail)) return "E-mail";
    const last = tail.replace(/^group_/, "").replace(/_(type|event)$/, "").replace(/_/g, " ");
    return last.charAt(0).toUpperCase() + last.slice(1);
  }

  // Uptime arrives as milliseconds (the Administrator client does `new Date(uptime)` in UTC); other text is left alone.
  _uptime(v) {
    if (v === null || v === undefined || !/^\d+$/.test(String(v).trim())) return v;
    const total = Math.floor(Number(v) / 1000), d = Math.floor(total / 86400), h = Math.floor(total % 86400 / 3600), m = Math.floor(total % 3600 / 60);
    const da = this._lang === "da";
    const days = `${d} ${da ? (d === 1 ? "dag" : "dage") : d === 1 ? "day" : "days"}`;
    const hours = `${h} ${da ? (h === 1 ? "time" : "timer") : h === 1 ? "hour" : "hours"}`;
    return `${d ? days + ", " : ""}${hours}, ${m} min`;
  }

  // The controller's WSDate ({year, monthWithJanuaryAsOne, day, hours, minutes, seconds}) as one line.
  _wsDate(v) {
    if (!v || typeof v !== "object" || Array.isArray(v) || !("year" in v) || !("monthWithJanuaryAsOne" in v)) return null;
    const p = (x) => String(x ?? 0).padStart(2, "0");
    return `${v.year}-${p(v.monthWithJanuaryAsOne)}-${p(v.day)} ${p(v.hours)}:${p(v.minutes)}:${p(v.seconds)}`;
  }

  // ------------------------------------------------------------------ already in the ihc integration

  // Resources that already are entities in the ihc integration, by id (registry + the user's YAML). Used for the flags.
  async _loadExisting() {
    try {
      const res = await this._ws({ type: "viewmyihc/entity/existing" });
      this._existing = new Map(Object.entries(res.by_id).map(([id, list]) => [Number(id), list]));
    } catch (_e) { /* the flags are a convenience; the dialog checks again when the YAML is made */ }
    if (this._tab === "project") this._renderTree();
    if (this._tab === "entities") this._renderCoverage();
    if (this._selected != null && this._detail) this._renderDetail();
  }

  _existingNames(id, platform) {
    return (this._existing.get(id) || []).filter((e) => !platform || e.platform === platform).map((e) => e.entity_id || e.name).join(", ");
  }

  _existingTitle(id) {
    return this.t("haChipTitle").replace("{list}", (this._existing.get(id) || []).map((e) => `${e.entity_id || e.name} (${this.tk("platform", e.platform)})`).join(", "));
  }

  // types that already have an entity for this resource (a second one would be rejected as a duplicate)
  _takenPlatforms(m) {
    return new Set((this._existing.get(m.id) || []).map((e) => e.platform));
  }

  _existingBox(id) {
    const list = this._existing.get(id);
    if (!list || !list.length) return "";
    const items = list.map((e) => `<li>
      <ha-icon icon="${PLATFORM_ICON[e.platform]}"></ha-icon>
      <span class="en">${e.entity_id
        ? `<button class="linkbtn" data-act="more-info" data-entity="${esc(e.entity_id)}" title="${esc(this.t("openEntity"))}">${esc(e.entity_id)}</button>`
        : `<strong>${esc(e.name)}</strong>`}
        <small>${esc(this.tk("platform", e.platform))}${e.source === "yaml" ? ` · ${esc(this.t("existsYaml").replace("{file}", e.file).replace("{line}", e.line))}` : ""}${e.disabled ? ` · ${esc(this.t("disabledTag"))}` : ""}</small></span>
    </li>`).join("");
    return `<div class="existbox"><ha-icon icon="mdi:home-assistant"></ha-icon><div><strong>${esc(this.t("existsTitle"))}</strong><ul>${items}</ul></div></div>`;
  }

  _existsNotice(m) {
    const list = this._existing.get(m.id) || [];
    if (!list.length) return "";
    const taken = this._takenPlatforms(m);
    const text = taken.size
      ? this.t("existsBlockedAll").replace("{list}", this._existingNames(m.id))
      : this.t("existsOther").replace("{list}", this._existingNames(m.id));
    return `<div class="callout ${taken.size ? "danger" : ""}"><ha-icon icon="mdi:home-assistant"></ha-icon><div><strong>${esc(this.t("existsTitle"))}</strong><p>${esc(text)}</p></div></div>`;
  }

  // ------------------------------------------------------------------ where the ihc setup lives (read only)

  async _runCheck() {
    if (this._checkBusy) return;
    this._checkBusy = true;
    if (this._tab === "entities") this._renderBody();
    try { this._check = await this._ws({ type: "viewmyihc/entity/check" }); this._checkError = ""; }
    catch (e) { this._check = null; this._checkError = (e && (e.message || e.code)) || String(e); }
    this._checkBusy = false;
    if (this._tab === "entities") this._renderBody();
  }

  _problemText(p) {
    return (this.t(`prob_${p.code}`) || p.code).replace(/\{(\w+)\}/g, (_m, k) => (p.params[k] ?? ""));
  }

  _checkCard() {
    const c = this._check;
    const head = `<h3>${esc(this.t("checkTitle"))}
      <button class="btn small right" data-act="run-check" ${this._checkBusy ? "disabled" : ""}>${esc(this._checkBusy ? this.t("checking") : this.t("checkAgain"))}</button></h3>`;
    if (!c) {
      return `<section class="card acard">${head}${this._checkError
        ? `<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(this._checkError)}</p>`
        : `<div class="skeleton"><i class="sk"></i><i class="sk s"></i></div>`}</section>`;
    }
    const kind = c.status === "ok" ? "ok" : "wait";
    const icon = c.status === "ok" ? "mdi:check-circle-outline" : "mdi:help-circle-outline";
    const code = (s) => `<code>${esc(s)}</code>`;
    let where = "";
    if (c.ihc_defined_in) {
      where = `<p class="help">${this.t("foundIn").replace("{file}", code(c.ihc_defined_in.file)).replace("{line}", c.ihc_defined_in.line)}`
        + (c.chosen && (c.chosen.file !== c.ihc_defined_in.file || c.chosen.line !== c.ihc_defined_in.line)
          ? ` ${this.t("controllerIn").replace("{file}", code(c.chosen.file)).replace("{line}", c.chosen.line)}` : "") + `</p>`;
    }
    const rows = Object.entries(c.platforms || {}).map(([p, info]) => {
      const n = info.entries.length;
      const loc = info.state === "missing" ? this.t("noList")
        : `${code(info.include || info.file)}${info.line && !info.include ? ":" + info.line : ""} · ${this.t("entryCount").replace("{n}", n)}`;
      return `<div class="prow"><ha-icon icon="${PLATFORM_ICON[p]}"></ha-icon><span class="pname">${esc(this.tk("platform", p))}</span><span class="ploc">${info.state === "missing" ? esc(loc) : loc}</span></div>`;
    }).join("");
    const problems = (c.problems || []).map((p) => `
      <li class="prob ${p.level}"><ha-icon icon="${p.level === "error" ? "mdi:alert-circle-outline" : p.level === "warn" ? "mdi:alert-outline" : "mdi:information-outline"}"></ha-icon>
        <span>${esc(this._problemText(p))}${p.file ? ` <code class="loc">${esc(p.file)}${p.line ? ":" + p.line : ""}</code>` : ""}</span></li>`).join("");
    return `<section class="card acard">${head}
      <div class="checkstatus ${kind}"><ha-icon icon="${icon}"></ha-icon><div><strong>${esc(this.tk("cstatus", c.status))}</strong>${where}</div></div>
      ${rows ? `<div class="prows">${rows}</div>` : ""}
      ${problems ? `<ul class="probs">${problems}</ul>` : ""}
      <p class="help foot"><ha-icon icon="mdi:lock-outline"></ha-icon>${esc(this.t("checkReadOnly"))}
        ${c.scanned?.length ? `<details><summary>${esc(this.t("scannedFiles").replace("{n}", c.scanned.length))}</summary><ul class="files">${c.scanned.map((f) => `<li><code>${esc(f)}</code></li>`).join("")}</ul></details>` : ""}</p>
    </section>`;
  }

  // ------------------------------------------------------------------ Entities tab: what exists in the ihc integration

  // ------------------------------------------------------------------ tools: modules, log, monitor, versions, coverage

  _when(epoch, withDate = false) {
    if (!epoch) return "–";
    const opts = withDate ? { dateStyle: "short", timeStyle: "medium" } : { hour: "2-digit", minute: "2-digit", second: "2-digit" };
    return new Date(epoch * 1000).toLocaleString(this._hass?.language || undefined, opts);
  }

  _downloadBlob(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  _toolError(text, act) {
    return `<div class="state card err"><h2>${esc(this.t("errorTitle"))}</h2><p>${esc(text)}</p>${act ? `<button class="btn" data-act="${act}">${esc(this.t("retry"))}</button>` : ""}</div>`;
  }

  // --- dataline modules

  // Like the admin tab: show the saved copy at once (Home Assistant answers from the project and its storage),
  // then read the controller in the background and redraw only if something changed.
  async _loadDataline() {
    if (!this._dl?.data) { this._dl = { loading: true }; if (this._tab === "modules") this._renderBody(); }
    try { this._dl = { data: await this._ws({ type: "viewmyihc/dataline" }) }; }
    catch (e) { this._dl = { error: this._errText(e) }; }
    if (this._tab === "modules") { this._renderBody(); this._schedule(true); }
    if (this._dl.data) this._refreshDataline();
  }

  async _refreshDataline() {
    const dl = this._dl; if (!dl?.data || dl.refreshing) return;
    dl.refreshing = true; this._renderDlStatus();
    try {
      const res = await this._ws({ type: "viewmyihc/dataline", refresh: true });
      const redraw = res.changed || res.controller_error !== dl.data.controller_error;
      if (res.changed && dl.data.saved) this._showToast(this.t("dlChanged"));
      dl.data = res; dl.checked = Date.now();
      if (redraw && this._tab === "modules" && this._dl === dl) this._renderBody();
    } catch (_e) { /* the saved copy stays; the status line says when it is from */ }
    dl.refreshing = false; this._renderDlStatus();
  }

  _renderDlStatus() {
    const el = this.shadowRoot.querySelector(".dl-status"); const dl = this._dl; if (!el || !dl?.data) return;
    el.innerHTML = dl.refreshing
      ? `<span class="spinner small"></span>${esc(this.t("dlChecking"))}`
      : dl.data.controller_error ? esc(this.t("dlCtlError"))
      : dl.data.saved ? esc(this.t("dlSavedAt").replace("{time}", this._clock(dl.data.saved))) : "";
  }

  _dlIds() {
    const d = this._dl?.data; if (!d) return [];
    return [...d.inputs, ...d.outputs].flatMap((line) => line.slots.filter((slot) => slot.name).map((slot) => slot.id));
  }

  // One block per dataline line: the module entered in IHC Visual decides which positions physically exist.
  _renderModules(body) {
    const dl = this._dl;
    if (!dl || dl.loading) { body.innerHTML = `<div class="state"><div class="spinner"></div><p>${esc(this.t("dlLoading"))}</p></div>`; return; }
    if (dl.error) { body.innerHTML = this._toolError(dl.error, "reload-dataline"); return; }
    const prefix = { inputs: "I", outputs: "O" };
    const section = (key, title) => {
      const lines = dl.data[key];
      const used = lines.reduce((n, l) => n + l.used, 0), all = lines.reduce((n, l) => n + l.capacity, 0);
      return `<section class="card acard"><h3>${esc(this.t(title))}<span class="chip">${esc(this.t("dlUsed").replace("{used}", used).replace("{all}", all))}</span></h3>
        ${lines.length ? lines.map((l) => `<div class="dl-block">
          <div class="dl-head"><b>${esc(this.t("dlLine").replace("{n}", l.line))}</b>
            <span class="${l.type ? "dl-type" : "dim"}">${esc(l.type || this.t("dlNoModule"))}</span>
            ${l.location ? `<span class="dim">· ${esc(l.location)}</span>` : ""}
            <span class="chip">${esc(this.t("dlUsed").replace("{used}", l.used - l.outside).replace("{all}", l.capacity))}</span>
            ${l.outside ? `<span class="chip err">${esc(this.t("dlOutsideChip").replace("{n}", l.outside))}</span>` : ""}</div>
          <div class="dl-grid">${l.slots.map((slot) => this._dlCell(slot, `${prefix[key]}${l.line}.${slot.position > 8 ? slot.position + 2 : "0" + slot.position}`)).join("")}</div></div>`).join("")
          : `<p class="dim">${esc(this.t("empty"))}</p>`}
      </section>`;
    };
    body.innerHTML = `<div class="project">
      <section class="panel mod-panel"><div class="mod-scroll">
        <div class="banner"><ha-icon icon="mdi:information-outline"></ha-icon><span class="grow">${esc(this.t("dlLead"))}</span></div>
        <div class="dl-bar"><span class="dl-status"></span><span class="grow"></span>
          <button class="btn small" data-act="reload-dataline">${esc(this.t("refreshAdmin"))}</button></div>
        ${section("inputs", "dlInputs")}${section("outputs", "dlOutputs")}</div></section>
      <aside class="panel detail-panel"></aside></div>`;
    this._renderDetail();
    this._paintValues();
    this._renderDlStatus();
  }

  _markDlSelected() {
    this.shadowRoot.querySelectorAll("[data-dlsel]").forEach((el) => el.classList.toggle("selected", Number(el.dataset.dlsel) === this._selected));
  }

  _dlCell(slot, place) {
    const where = `${place} · ${this.t("dlAddress")} ${slot.address}${slot.id ? ` · ID ${slot.id}` : ""}`;
    if (!slot.name) return `<div class="dl-cell free" title="${esc(where)}"><span class="dl-addr">${esc(place)}</span><span class="dim">${esc(this.t("dlFree"))}</span></div>`;
    const f = this._values.has(slot.id) ? this.fmt(slot.kind, this._values.get(slot.id)) : { text: "", cls: "none" };
    const note = !slot.usable ? this.t("dlOutside") : slot.links ? "" : this.t("covUnlinked");
    return `<button class="dl-cell ${slot.usable ? "" : "outside"} ${slot.links ? "" : "unlinked"} ${this._selected === slot.id ? "selected" : ""}" data-dlsel="${slot.id}" title="${esc(`${slot.label} · ${where}${note ? " · " + note : ""}`)}">
      <span class="dl-addr">${esc(place)}</span><span class="dl-name">${esc(slot.name)}</span><small>${esc(slot.product || "")}</small>
      <span class="val ${f.cls}" data-val="${slot.id}" data-kind="${esc(slot.kind || "bool")}">${esc(f.text)}</span></button>`;
  }

  // --- log tab: controller log, messages, live monitor

  _openLog() {
    this._logView = this._logView || "userlog";
    if (this._logView === "userlog" && !this._ulog) this._loadUserLog();
    if (this._logView === "messages" && !this._msgs) this._loadMessages();
    if (this._logView === "monitor") this._monitorPoll(true);
  }

  async _loadUserLog() {
    this._ulog = { loading: true }; this._renderLogBody();
    try { this._ulog = { lines: (await this._ws({ type: "viewmyihc/log", language: this._lang })).lines, at: Date.now() / 1000 }; }
    catch (e) { this._ulog = { error: this._errText(e) }; }
    this._renderLogBody();
  }

  async _loadMessages() {
    this._msgs = { loading: true }; this._renderLogBody();
    try { this._msgs = await this._ws({ type: "viewmyihc/messages" }); }
    catch (e) { this._msgs = { error: this._errText(e) }; }
    this._renderLogBody();
  }

  _renderLog(body) {
    this._logView = this._logView || "userlog";
    const views = ["userlog", "messages", "monitor"].map((v) =>
      `<button class="seg ${this._logView === v ? "active" : ""}" data-logview="${v}">${esc(this.t("log_" + v))}</button>`).join("");
    body.innerHTML = `<div class="tools"><div class="toolbar flat"><div class="segmented" role="group">${views}</div>
      <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input type="search" data-logq placeholder="${esc(this.t("logSearch"))}" value="${esc(this._logQ || "")}" /></label></div>
      <div class="logbody"></div></div>`;
    body.querySelector("[data-logq]").addEventListener("input", (e) => { this._logQ = e.target.value; this._renderLogBody(); });
    this._renderLogBody();
  }

  _logMatch(text) {
    const q = (this._logQ || "").trim().toLowerCase();
    return !q || String(text).toLowerCase().includes(q);
  }

  _renderLogBody() {
    const el = this.shadowRoot.querySelector(".logbody"); if (!el || this._tab !== "log") return;
    if (this._logView === "userlog") el.innerHTML = this._userLogHtml();
    else if (this._logView === "messages") el.innerHTML = this._messagesHtml();
    else el.innerHTML = this._monitorHtml();
    this._paintValues();
  }

  _userLogHtml() {
    const u = this._ulog;
    if (!u || u.loading) return `<div class="state"><div class="spinner"></div></div>`;
    if (u.error) return this._toolError(u.error, "reload-log");
    let lines = u.lines.filter((l) => this._logMatch(l));
    if (this._logNewest) lines = [...lines].reverse();
    const warn = /batter|fejl|error|fail|alarm|ikke tilknyttet|not assigned/i;
    return `<section class="card acard"><h3>${esc(this.t("log_userlog"))}<span class="chip">${lines.length}/${u.lines.length}</span>
        <span class="right"><button class="btn-text small" data-act="log-order">${esc(this.t(this._logNewest ? "logOldestFirst" : "logNewestFirst"))}</button>
        ${this._clearButton("userlog")}<button class="btn small" data-act="reload-log">${esc(this.t("refreshAdmin"))}</button></span></h3>
      <p class="help">${esc(this.t("logLead"))}</p>${this._clearBox("userlog")}
      ${lines.length ? `<ol class="loglines">${lines.map((l) => `<li class="${warn.test(l) ? "warn" : ""}">${esc(l)}</li>`).join("")}</ol>` : `<p class="dim">${esc(this.t("logEmpty"))}</p>`}
    </section>`;
  }

  _clearButton(what) {
    return `<button class="btn-text small danger" data-act="log-clear" data-what="${what}"><ha-icon icon="mdi:delete-sweep-outline"></ha-icon>${esc(this.t("logClear"))}</button>`;
  }

  // Emptying a log on the controller cannot be undone: it needs the ihc login password, like admin changes.
  _clearBox(what) {
    const c = this._logClear; if (!c || c.what !== what) return "";
    return `<div class="clearbox"><p>${esc(this.t("logClearAsk"))}</p>
      <label class="field auth"><span class="lbl2"><ha-icon icon="mdi:shield-key-outline"></ha-icon>${esc(this.t("adminAuth").replace("{user}", this._haUser || "ihc"))}</span>
        <input type="password" autocomplete="current-password" data-clearauth value="" /></label>
      ${c.error ? `<p class="ferr box">${esc(c.error)}</p>` : ""}
      <div class="formfoot"><span class="grow"></span><button class="btn-text" data-act="log-clear-cancel" ${c.busy ? "disabled" : ""}>${esc(this.t("cancel"))}</button>
        <button class="btn small danger" data-act="log-clear-go" ${c.busy ? "disabled" : ""}>${esc(c.busy ? this.t("saving") : this.t("logClear"))}</button></div></div>`;
  }

  async _clearLog() {
    const c = this._logClear; if (!c) return;
    const auth = this.shadowRoot.querySelector("[data-clearauth]")?.value || "";
    if (!auth) { c.error = this.t("adminAuthMissing"); this._renderLogBody(); return; }
    c.busy = true; c.error = ""; this._renderLogBody();
    try {
      await this._ws({ type: "viewmyihc/log/clear", what: c.what, auth });
      this._logClear = null;
      this._showToast(this.t("logCleared"));
      if (c.what === "userlog") this._loadUserLog(); else this._loadMessages();
      return;
    } catch (err) {
      c.error = err && err.code === "wrong_password"
        ? (/many/i.test(err.message || "") ? this.t("adminAuthLocked") : this.t("adminAuthWrong")) : this._errText(err);
    }
    c.busy = false; this._renderLogBody();
  }

  // SceneDesign's own setup: messages on resource changes, and control of the controller by e-mail/SMS (read-only).
  async _loadScene(refresh = false) {
    this._scene = { ...(this._scene || {}), loading: true, error: "" }; this._paintScene();
    try { this._scene = { data: await this._ws({ type: "viewmyihc/scene/messages", refresh }) }; }
    catch (e) { this._scene = { error: this._errText(e) }; }
    this._paintScene();
  }

  // only the card itself is redrawn, so an admin form being filled in is never touched
  _paintScene() {
    const el = this.shadowRoot.querySelector(".admin-scene"); if (el) el.innerHTML = this._sceneHtml();
  }

  _sceneHtml() {
    const sc = this._scene;
    const head = `<h3>${esc(this.t("scTitle"))}<span class="right"><button class="btn small" data-act="scene-reload" ${sc?.loading ? "disabled" : ""}>${esc(this.t("refreshAdmin"))}</button></span></h3>
      <p class="help">${esc(this.t("scLead"))}</p>`;
    if (!sc || sc.loading && !sc.data) return `<section class="card acard">${head}<div class="spinner small"></div></section>`;
    if (sc.error) return `<section class="card acard">${head}<p class="ferr box">${esc(sc.error)}</p></section>`;
    const d = sc.data;
    const res = (r) => r?.label ? `<button class="linkbtn" data-jump="${r.id}">${esc(r.name)}</button><small>${esc(r.label)}</small>` : `<code>${r?.id ?? "?"}</code>`;
    const who = (list) => list.map((x) => typeof x === "string" ? esc(x)
      : `<span class="slot" title="${esc(this.t("scSlot").replace("{n}", x.slot))}">${esc(x.label || this.t("scSlot").replace("{n}", x.slot))}${x.number ? ` <small>${esc(x.number)}</small>` : ""}</span>`).join("<br>") || "–";
    const chan = (c) => `<span class="chip">${c === "sms" ? "SMS" : "E-mail"}</span>`;
    const notes = d.notifications, ctls = d.controls;
    return `<section class="card acard">${head}
      <h4>${esc(this.t("scNotifications"))} <span class="chip">${notes.length}</span></h4>
      ${notes.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("scResource"))}</th><th>${esc(this.t("scWhen"))}</th><th></th><th>${esc(this.t("scTo"))}</th><th>${esc(this.t("scMessage"))}</th></tr></thead><tbody>
        ${notes.map((n) => `<tr><td>${res(n.resource)}</td><td>${esc(this.tk("scEvent", n.event))}</td><td>${chan(n.channel)}</td>
          <td>${who(n.channel === "sms" ? n.slots : n.recipients)}</td><td>${n.subject ? `<b>${esc(n.subject)}</b><br>` : ""}${esc(n.body)}</td></tr>`).join("")}</tbody></table></div>`
        : `<p class="dim">${esc(this.t("msgNone"))}</p>`}
      <h4>${esc(this.t("scControls"))} <span class="chip">${ctls.length}</span></h4>
      ${ctls.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("colCommand"))}</th><th></th><th>${esc(this.t("scDoes"))}</th><th>${esc(this.t("scAuth"))}</th><th>${esc(this.t("scFrom"))}</th></tr></thead><tbody>
        ${ctls.map((c) => `<tr><td><code>${esc(c.trigger)}</code></td><td>${chan(c.channel)}</td>
          <td>${esc(this.tk("scAction", c.action))} ${res(c.resource)}${c.confirmation ? `<small>${esc(this.t("scReply"))}: ${esc(c.confirmation)}</small>` : ""}</td>
          <td>${esc(this.tk("scAuthType", c.authorization))}</td>
          <td>${c.authorization === "three_way" ? `${esc(this.t("scConfirmTo"))}: ${esc(c.confirmation_address || "–")}` : c.authorization === "direct_control" ? esc(this.t("scAnyone")) : who(c.senders)}</td></tr>`).join("")}</tbody></table></div>`
        : `<p class="dim">${esc(this.t("msgNone"))}</p>`}
      <p class="help">${esc(this.t("scEditNote"))}</p></section>`;
  }

  _messagesHtml() {
    const m = this._msgs;
    if (!m || m.loading) return `<div class="state"><div class="spinner"></div></div>`;
    if (m.error) return this._toolError(m.error, "reload-messages");
    const date = (d) => esc(this._wsDate(d) ?? "–");
    const sent = (m.notifications || []).filter((n) => this._logMatch(JSON.stringify(n)));
    const ctl = (m.control || []).filter((n) => this._logMatch(JSON.stringify(n)));
    const err = (k) => (m.errors?.[k] ? `<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(m.errors[k])}</p>` : "");
    return `<section class="card acard"><h3>${esc(this.t("msgSent"))}<span class="chip">${sent.length}</span>
        <span class="right">${this._clearButton("messages")}<button class="btn small" data-act="reload-messages">${esc(this.t("refreshAdmin"))}</button></span></h3>
      ${this._clearBox("messages")}${err("notifications")}
      ${sent.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("colTime"))}</th><th>${esc(this.t("colType"))}</th><th>${esc(this.t("colTo"))}</th><th>${esc(this.t("colSubject"))}</th><th>${esc(this.t("colDelivered"))}</th></tr></thead><tbody>
        ${sent.map((n) => `<tr title="${esc(n.body || "")}"><td>${date(n.date)}</td><td>${esc(this._adminValue("type", n.notificationType || ""))}</td><td>${esc(n.recipient || "")}</td><td>${esc(n.subject || "")}</td>
          <td>${n.delivered === "true" ? `<span class="chip ok">✓</span>` : `<span class="chip err">✗</span>`}</td></tr>`).join("")}</tbody></table></div>` : `<p class="dim">${esc(this.t("msgNone"))}</p>`}
    </section>
    <section class="card acard"><h3>${esc(this.t("msgControl"))}<span class="chip">${ctl.length}</span>
        ${m.control_disabled ? "" : `<span class="right">${this._clearButton("control")}</span>`}</h3><p class="help">${esc(this.t("msgControlLead"))}</p>
      ${this._clearBox("control")}${err("control")}
      ${m.control_disabled ? `<p class="dim">${esc(this.t("msgControlOff"))}</p>` : ctl.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("colTime"))}</th><th>${esc(this.t("colType"))}</th><th>${esc(this.t("colFrom"))}</th><th>${esc(this.t("colCommand"))}</th><th>${esc(this.t("colResult"))}</th></tr></thead><tbody>
        ${ctl.map((n) => `<tr><td>${date(n.date)}</td><td>${esc(this._adminValue("type", n.controlType || ""))}</td><td>${esc(typeof n.senderAddress === "object" && n.senderAddress ? Object.values(n.senderAddress).filter(Boolean).join(" ") : n.senderAddress || "")}</td>
          <td>${esc(n.triggerString || "")}</td><td>${esc([n.actionTypeAsString, n.authenticationTypeAsString].filter(Boolean).map((x) => this._adminValue("type", x)).join(" · "))}</td></tr>`).join("")}</tbody></table></div>` : `<p class="dim">${esc(this.t("msgNone"))}</p>`}
    </section>`;
  }

  _monitorHtml() {
    const mon = this._mon;
    if (!mon || !mon.started) {
      return `<section class="card acard"><h3>${esc(this.t("log_monitor"))}</h3><p>${esc(this.t("monLead"))}</p>
        <p class="help">${esc(this.t("monNote"))}</p>
        ${mon?.error ? `<p class="ferr box">${esc(mon.error)}</p>` : ""}
        <button class="btn" data-act="monitor-start" ${mon?.busy ? "disabled" : ""}><ha-icon icon="mdi:play"></ha-icon> ${esc(mon?.busy ? this.t("monStarting") : this.t("monStart"))}</button></section>`;
    }
    const rows = mon.events.filter((e) => this._logMatch(`${e.name || ""} ${e.label || ""} ${e.id}`));
    return `<section class="card acard"><h3>${esc(this.t("log_monitor"))}<span class="chip">${rows.length}</span>
        <span class="right"><button class="btn-text small" data-act="monitor-pause">${esc(this.t(mon.paused ? "monResume" : "monPause"))}</button>
        <button class="btn-text small" data-act="monitor-csv" ${mon.events.length ? "" : "disabled"}>CSV</button>
        <button class="btn-text small" data-act="monitor-clear">${esc(this.t("monClear"))}</button></span></h3>
      <p class="help">${esc(this.t("monWatching").replace("{n}", mon.watching).replace("{time}", this._when(mon.started, true)))}</p>
      ${rows.length ? `<div class="tablewrap"><table class="tbl mon"><thead><tr><th>${esc(this.t("colTime"))}</th><th>${esc(this.t("name"))}</th><th>${esc(this.t("monChange"))}</th></tr></thead><tbody>
        ${rows.slice(0, 500).map((e) => {
          const a = this.fmt(e.kind, e.old), b = this.fmt(e.kind, e.new);
          return `<tr class="jumprow" data-jump="${e.id}"><td class="nowrap">${esc(this._when(e.time))}</td><td><strong>${esc(e.name || e.id)}</strong><small>${esc(e.label || "")}</small></td>
            <td class="nowrap"><span class="val ${a.cls}">${esc(a.text)}</span> → <span class="val ${b.cls}">${esc(b.text)}</span></td></tr>`;
        }).join("")}</tbody></table></div>` : `<p class="dim">${esc(this.t("monNone"))}</p>`}
    </section>`;
  }

  async _monitorStart() {
    this._mon = { ...(this._mon || {}), busy: true, error: "" }; this._renderLogBody();
    try {
      const res = await this._ws({ type: "viewmyihc/monitor/start" });
      this._mon = { started: res.started, watching: res.watching, events: [], seq: 0, paused: false };
    } catch (e) { this._mon = { error: this._errText(e) }; }
    this._renderLogBody(); this._monitorPoll(true);
  }

  // Fetch new changes every second while the monitor is on screen.
  async _monitorPoll(first = false) {
    clearTimeout(this._monTimer);
    const onScreen = this._tab === "log" && this._logView === "monitor" && this.isConnected && !document.hidden;
    if (!onScreen) return;
    const mon = this._mon;
    if (!mon || (mon.started && !mon.paused) || first) {
      try {
        const res = await this._ws({ type: "viewmyihc/monitor/events", after: mon?.seq || 0 });
        if (res.started) {
          const m = this._mon && this._mon.started ? this._mon : (this._mon = { events: [], seq: 0, paused: false });
          Object.assign(m, { started: res.started, watching: res.watching });
          if (res.events.length) {
            m.events = [...res.events.reverse(), ...m.events].slice(0, 2000);
            m.seq = Math.max(m.seq, ...res.events.map((e) => e.seq));
            this._renderLogBody();
          } else if (first) this._renderLogBody();
        } else if (first) this._renderLogBody();
      } catch (_e) { /* the next tick tries again */ }
    }
    this._monTimer = setTimeout(() => this._monitorPoll(), 1000);
  }

  _monitorCsv() {
    const q = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const rows = [["time", "id", "name", "location", "before", "after"].join(";"),
      ...[...this._mon.events].reverse().map((e) => [new Date(e.time * 1000).toISOString(), e.id, q(e.name), q(e.label), q(e.old), q(e.new)].join(";"))];
    this._downloadBlob(new Blob([rows.join("\r\n")], { type: "text/csv" }), `ihc-monitor-${new Date().toISOString().slice(0, 19).replace(/:/g, "")}.csv`);
  }

  // --- versions: backups and what changed

  async _loadBackups() {
    const kind = this._bkKind || "ihc";
    this._bk = { loading: true, kind }; if (this._tab === "versions") this._renderBody();
    try {
      const res = await this._ws({ type: "viewmyihc/backups", kind });
      const list = res.backups;
      this._bk = { kind, list, warn: res.error || "", from: list[1]?.name || null, to: list[0]?.name || null };
      if (kind === "ihc" && list.length > 1) this._compareBackups();
    } catch (e) { this._bk = { kind, error: this._errText(e) }; }
    if (this._tab === "versions") this._renderBody();
  }

  async _compareBackups() {
    const bk = this._bk; if (!bk?.from || !bk?.to) return;
    bk.diff = { loading: true }; this._renderVersionsDiff();
    try { bk.diff = await this._ws({ type: "viewmyihc/backup/diff", old: bk.from, new: bk.to }); }
    catch (e) { bk.diff = { error: this._errText(e) }; }
    this._renderVersionsDiff();
  }

  async _downloadBackup(name) {
    try {
      if (/\.icz$/.test(name)) {  // a SceneDesign project is a zip already
        const res = await this._ws({ type: "viewmyihc/backup/download", name, kind: "scene" });
        this._downloadBlob(new Blob([Uint8Array.from(atob(res.data), (c) => c.charCodeAt(0))], { type: "application/zip" }), res.name);
        return;
      }
      const res = await this._ws({ type: "viewmyihc/backup/download", name });
      const bytes = Uint8Array.from(atob(res.gzip), (c) => c.charCodeAt(0));
      const plain = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).blob();
      this._downloadBlob(plain, res.name);
    } catch (e) { this._showToast(this._errText(e)); }
  }

  _renderVersions(body) {
    const bk = this._bk;
    if (!bk || bk.loading) { body.innerHTML = `<div class="state"><div class="spinner"></div></div>`; return; }
    if (bk.error) { body.innerHTML = this._toolError(bk.error, "reload-backups"); return; }
    const opt = (sel) => bk.list.map((b) => `<option value="${esc(b.name)}" ${b.name === sel ? "selected" : ""}>${esc(this._when(b.saved, true))}${b.modified ? ` · ${esc(this.t("modified"))} ${esc(b.modified)}` : ""}</option>`).join("");
    const kinds = ["ihc", "scene"].map((k) => `<button class="seg ${bk.kind === k ? "active" : ""}" data-bkkind="${k}">${esc(this.t("bkKind_" + k))}</button>`).join("");
    const size = (b) => (b.size >= 1048576 ? (b.size / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(b.size / 1024)) + " kB");
    if (bk.kind === "scene") {
      body.innerHTML = `<div class="tools"><div class="toolbar flat"><div class="segmented" role="group">${kinds}</div></div>
        <div class="banner"><ha-icon icon="mdi:shield-lock-outline"></ha-icon><span class="grow">${esc(this.t("bkSceneLead"))}</span></div>
        <section class="card acard"><h3>${esc(this.t("bkKind_scene"))}<span class="chip">${bk.list.length}</span>
          <button class="btn small right" data-act="reload-backups">${esc(this.t("refreshAdmin"))}</button></h3>
          ${bk.warn ? `<p class="adm-err"><ha-icon icon="mdi:alert-outline"></ha-icon>${esc(bk.warn)}</p>` : ""}
          ${bk.list.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("bkSaved"))}</th><th>${esc(this.t("name"))}</th>
            <th>${esc(this.t("bkSceneScenes"))}</th><th>${esc(this.t("scNotifications"))}</th><th>${esc(this.t("scControls"))}</th><th>${esc(this.t("bkSize"))}</th><th></th></tr></thead><tbody>
            ${bk.list.map((b) => `<tr><td>${esc(this._when(b.saved, true))}</td><td>${esc(b.scene_name || "–")}</td><td>${esc(b.scenes ?? "–")}</td>
              <td>${esc(b.notifications ?? "–")}</td><td>${esc(b.controls ?? "–")}</td><td>${size(b)}</td>
              <td><button class="btn-text small" data-act="backup-download" data-name="${esc(b.name)}"><ha-icon icon="mdi:download"></ha-icon> .icz</button></td></tr>`).join("")}</tbody></table></div>`
            : `<p class="dim">${esc(this.t("bkNone"))}</p>`}
        </section></div>`;
      return;
    }
    body.innerHTML = `<div class="tools"><div class="toolbar flat"><div class="segmented" role="group">${kinds}</div></div>
      <div class="banner"><ha-icon icon="mdi:shield-lock-outline"></ha-icon><span class="grow">${esc(this.t("bkLead"))}</span></div>
      <section class="card acard"><h3>${esc(this.t("bkTitle"))}<span class="chip">${bk.list.length}</span>
        <button class="btn small right" data-act="reload-backups">${esc(this.t("refreshAdmin"))}</button></h3>
        ${bk.list.length ? `<div class="tablewrap"><table class="tbl"><thead><tr><th>${esc(this.t("bkSaved"))}</th><th>${esc(this.t("modified"))}</th><th>${esc(this.t("resources"))}</th><th>${esc(this.t("bkSize"))}</th><th></th></tr></thead><tbody>
          ${bk.list.map((b) => `<tr><td>${esc(this._when(b.saved, true))}</td><td>${esc(b.modified || "–")}</td><td>${esc(b.resources ?? "–")}</td><td>${size(b)}</td>
            <td><button class="btn-text small" data-act="backup-download" data-name="${esc(b.name)}"><ha-icon icon="mdi:download"></ha-icon> .vis</button></td></tr>`).join("")}</tbody></table></div>`
          : `<p class="dim">${esc(this.t("bkNone"))}</p>`}
      </section>
      ${bk.list.length > 1 ? `<section class="card acard"><h3>${esc(this.t("bkCompare"))}</h3>
        <div class="cmp"><label class="field"><span class="lbl2">${esc(this.t("bkFrom"))}</span><select data-bk="from">${opt(bk.from)}</select></label>
          <ha-icon icon="mdi:arrow-right"></ha-icon>
          <label class="field"><span class="lbl2">${esc(this.t("bkTo"))}</span><select data-bk="to">${opt(bk.to)}</select></label></div>
        <div class="diffbody"></div></section>` : ""}</div>`;
    body.querySelectorAll("[data-bk]").forEach((s) => s.addEventListener("change", () => { bk[s.dataset.bk] = s.value; this._compareBackups(); }));
    this._renderVersionsDiff();
  }

  _renderVersionsDiff() {
    const el = this.shadowRoot.querySelector(".diffbody"); const d = this._bk?.diff; if (!el || !d) return;
    if (d.loading) { el.innerHTML = `<div class="spinner small"></div>`; return; }
    if (d.error) { el.innerHTML = `<p class="ferr box">${esc(d.error)}</p>`; return; }
    const c = d.counts;
    if (!c.added && !c.removed && !c.changed) { el.innerHTML = `<p class="dim">${esc(this.t("bkSame"))}</p>`; return; }
    const item = (n, extra = "") => `<li><button class="link-item" data-jump="${n.id}"><ha-icon icon="${iconFor({ category: n.category, kind: n.kind, tag: "" })}"></ha-icon>
      <span><strong>${esc(n.name)}</strong><small>${esc(n.label)}</small>${extra}</span><code>${n.id}</code></button></li>`;
    const field = (ch) => ch.field === "links"
      ? `<div class="chg-line"><b>${esc(this.t("links"))}:</b> ${ch.added.map((x) => `<span class="plus">+ ${esc(x.replace(/^\w+:/, ""))}</span>`).join(" ")} ${ch.removed.map((x) => `<span class="minus">− ${esc(x.replace(/^\w+:/, ""))}</span>`).join(" ")}</div>`
      : `<div class="chg-line"><b>${esc(ch.field === "name" ? this.t("name") : ch.field === "location" ? this.t("path") : humanize(ch.field))}:</b> <span class="minus">${esc(ch.old ?? "–")}</span> → <span class="plus">${esc(ch.new ?? "–")}</span></div>`;
    const more = (shown, all) => (all > shown ? `<p class="dim small">${esc(this.t("bkMore").replace("{n}", all - shown))}</p>` : "");
    el.innerHTML = `<div class="diffcounts"><span class="chip ok">+ ${c.added} ${esc(this.t("bkAdded"))}</span><span class="chip err">− ${c.removed} ${esc(this.t("bkRemoved"))}</span><span class="chip chg">${c.changed} ${esc(this.t("bkChanged"))}</span></div>
      ${d.changed.length ? `<h3>${esc(this.t("bkChanged"))}</h3><ul class="links">${d.changed.map((n) => item(n, n.changes.map(field).join(""))).join("")}</ul>${more(d.changed.length, c.changed)}` : ""}
      ${d.added.length ? `<h3>${esc(this.t("bkAdded"))}</h3><ul class="links">${d.added.map((n) => item(n)).join("")}</ul>${more(d.added.length, c.added)}` : ""}
      ${d.removed.length ? `<h3>${esc(this.t("bkRemoved"))}</h3><ul class="links removed-list">${d.removed.map((n) => `<li class="link-item internal"><span><strong>${esc(n.name)}</strong><small>${esc(n.label)}</small></span><code>${n.id}</code></li>`).join("")}</ul>${more(d.removed.length, c.removed)}` : ""}`;
  }

  // --- coverage (entities tab)

  async _loadCoverage() {
    try { this._cov = (await this._ws({ type: "viewmyihc/coverage" })).resources; this._covError = ""; }
    catch (e) { this._cov = null; this._covError = this._errText(e); }
    if (this._tab === "entities") this._renderCoverage();
  }

  _coverageCard() { return `<section class="card acard covcard"></section>`; }

  _renderCoverage() {
    const el = this.shadowRoot.querySelector(".covcard"); if (!el) return;
    if (!this._cov) { el.innerHTML = this._covError ? `<h3>${esc(this.t("covTitle"))}</h3><p class="ferr box">${esc(this._covError)}</p>` : `<h3>${esc(this.t("covTitle"))}</h3><div class="spinner small"></div>`; return; }
    const f = this._covFilter || "missing";
    const has = (r) => this._existing.has(r.id);
    const covQ = (this._covQ || "").trim().toLowerCase();
    const all = this._cov, withEntity = all.filter(has).length, unlinked = all.filter((r) => !r.links).length;
    const rows = all.filter((r) => (f === "missing" ? !has(r) : f === "unlinked" ? !r.links : true))
      .filter((r) => !covQ || `${r.name} ${r.label} ${r.id}`.toLowerCase().includes(covQ));
    const groups = new Map();
    for (const r of rows) {
      const key = r.owner === "product" ? `p:${r.tag}` : `f:${r.section || ""}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    }
    const title = (key) => {
      const [kind, tag] = key.split(":");
      if (kind === "p") return this.tk("covTag", tag) || tag;
      return `${this.t("covBlocks")}: ${this.tk("covSection", tag) || tag}`;
    };
    const segs = [["missing", this.t("covMissing"), all.length - withEntity], ["unlinked", this.t("covUnlinked"), unlinked], ["all", this.t("allTypes"), all.length]]
      .map(([k, label, n]) => `<button class="seg ${f === k ? "active" : ""}" data-covfilter="${k}">${esc(label)} <b>${n}</b></button>`).join("");
    el.innerHTML = `<h3>${esc(this.t("covTitle"))}<span class="chip">${esc(this.t("covSummary").replace("{n}", withEntity).replace("{all}", all.length))}</span></h3>
      <p class="help">${esc(this.t("covLead"))}</p>
      <div class="toolbar flat"><div class="segmented" role="group">${segs}</div>
        <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input type="search" data-covq placeholder="${esc(this.t("entSearch"))}" value="${esc(this._covQ || "")}" /></label></div>
      ${rows.length ? [...groups.entries()].map(([key, list]) => `<details class="covgroup" ${groups.size <= 3 ? "open" : ""}><summary>${esc(title(key))} <span class="chip">${list.length}</span></summary>
        ${list.slice(0, 300).map((r) => `<div class="erow"><ha-icon class="eico" icon="${iconFor({ category: "resource", kind: r.kind, tag: r.tag })}"></ha-icon>
          <div class="einfo"><div class="ename">${esc(r.name)}</div><div class="esub">${esc(r.label)} · <code>${r.id}</code></div></div>
          ${has(r) ? `<span class="chip ha"><ha-icon icon="mdi:home-assistant"></ha-icon></span>` : ""}
          ${r.links ? `<span class="chip link"><ha-icon icon="mdi:link-variant"></ha-icon>${r.links}</span>` : `<span class="chip wait">${esc(this.t("covNoLinks"))}</span>`}
          <button class="icon-btn" data-act="show-in-tree" data-id="${r.id}" title="${esc(this.t("showInTree"))}"><ha-icon icon="mdi:file-tree"></ha-icon></button>
          ${has(r) ? "" : `<button class="icon-btn" data-act="create-entity" data-id="${r.id}" title="${esc(this.t("createEntity"))}"><ha-icon icon="mdi:plus-circle-outline"></ha-icon></button>`}</div>`).join("")}
        ${list.length > 300 ? `<p class="dim small">${esc(this.t("bkMore").replace("{n}", list.length - 300))}</p>` : ""}</details>`).join("")
        : `<p class="dim">${esc(this.t("entNone"))}</p>`}`;
    const q = el.querySelector("[data-covq]");
    q.addEventListener("input", (e) => { this._covQ = e.target.value; clearTimeout(this._covTimer); this._covTimer = setTimeout(() => { this._renderCoverage(); const n = this.shadowRoot.querySelector("[data-covq]"); if (n) { n.focus(); n.setSelectionRange(n.value.length, n.value.length); } }, 200); });
  }

  // --- press automation (detail panel, push buttons)

  _isButton(d) { return d && d.kind === "bool" && /input$/.test(d.tag); }

  _pressHtml(d) {
    if (!this._isButton(d)) return "";
    const sensors = (this._existing.get(d.id) || []).filter((e) => e.platform === "binary_sensor" && e.entity_id);
    const p = this._press && this._press.id === d.id ? this._press : { id: d.id, long: 800, double: 400, entity: sensors[0]?.entity_id || "" };
    this._press = p;
    const body = !sensors.length
      ? `<p class="help">${esc(this.t("pressNeedsSensor"))}</p>`
      : `${sensors.length > 1 ? `<label class="field"><span class="lbl2">${esc(this.t("entities"))}</span><select data-press="entity">${sensors.map((e) => `<option ${e.entity_id === p.entity ? "selected" : ""}>${esc(e.entity_id)}</option>`).join("")}</select></label>` : ""}
        <div class="two"><label class="field"><span class="lbl2">${esc(this.t("pressLong"))}</span><input type="number" min="200" max="5000" step="50" data-press="long" value="${p.long}" /></label>
          <label class="field"><span class="lbl2">${esc(this.t("pressDouble"))}</span><input type="number" min="100" max="2000" step="50" data-press="double" value="${p.double}" /></label></div>
        <button class="btn small" data-act="press-make">${esc(this.t("pressMake"))}</button>
        ${p.error ? `<p class="ferr box">${esc(p.error)}</p>` : ""}
        ${p.yaml ? `<div class="codebox"><button class="btn small" data-act="press-copy">${esc(this.t("copyYaml"))}</button><pre>${esc(p.yaml)}</pre></div>
          <p class="help">${esc(this.t("pressHow"))}</p>` : ""}`;
    return `<details class="press" ${p.open ? "open" : ""}><summary><ha-icon icon="mdi:gesture-double-tap"></ha-icon>${esc(this.t("pressTitle"))}</summary>
      <p class="help">${esc(this.t("pressLead"))}</p>${body}</details>`;
  }

  async _pressMake() {
    const p = this._press, d = this._detail; if (!p || !d) return;
    const root = this.shadowRoot;
    p.long = Number(root.querySelector('[data-press="long"]')?.value || p.long);
    p.double = Number(root.querySelector('[data-press="double"]')?.value || p.double);
    p.entity = root.querySelector('[data-press="entity"]')?.value || p.entity;
    p.open = true; p.error = "";
    try { p.yaml = (await this._ws({ type: "viewmyihc/press", entity_id: p.entity, name: d.name, long_ms: p.long, double_ms: p.double, language: this._lang })).yaml; }
    catch (e) { p.yaml = ""; p.error = this._errText(e); }
    this._renderDetail();
  }

  // ------------------------------------------------------------------ settings

  async _loadSettings() {
    try { this._set = { ...(await this._ws({ type: "viewmyihc/settings/get" })), error: "" }; }
    catch (e) { this._set = { error: this._errText(e) }; }
    this._set.form = { ...(this._set.settings || {}) };
    if (this._tab === "settings") this._renderBody();
  }

  async _saveSettings() {
    const st = this._set; if (!st?.form) return;
    st.busy = true; st.error = ""; this._renderBody();
    try {
      const res = await this._ws({ type: "viewmyihc/settings/set", ihc_timeout: !!st.form.ihc_timeout, ihc_timeout_seconds: Number(st.form.ihc_timeout_seconds) });
      this._set = { ...res, form: { ...res.settings }, error: "" };
      this._showToast(this.t("setSaved"));
    } catch (e) { st.error = this._errText(e); st.busy = false; }
    this._renderBody();
  }

  _renderSettings(body) {
    const st = this._set;
    if (!st) { body.innerHTML = `<div class="state"><div class="spinner"></div></div>`; return; }
    if (!st.form) { body.innerHTML = this._toolError(st.error, "reload-settings"); return; }
    const f = st.form, lim = st.limits || { min: 15, max: 300 };
    const active = Object.entries(st.active || {});
    body.innerHTML = `<div class="tools settings">
      <section class="card acard"><h3>${esc(this.t("setConnTitle"))}</h3>
        <p class="help">${esc(this.t("setConnLead"))}</p>
        <label class="switchrow"><input type="checkbox" data-setf="ihc_timeout" ${f.ihc_timeout ? "checked" : ""}/><span>${esc(this.t("setTimeout"))}</span></label>
        <label class="field"><span class="lbl2">${esc(this.t("setSeconds").replace("{min}", lim.min).replace("{max}", lim.max))}</span>
          <input type="number" min="${lim.min}" max="${lim.max}" step="5" data-setf="ihc_timeout_seconds" value="${esc(f.ihc_timeout_seconds)}" ${f.ihc_timeout ? "" : "disabled"}/></label>
        <div class="setstatus">${active.length ? active.map(([serial, t]) => `<div class="${t ? "on" : "off"}"><ha-icon icon="${t ? "mdi:shield-check-outline" : "mdi:shield-off-outline"}"></ha-icon>
          ${esc(t ? this.t("setActive").replace("{s}", t) : this.t("setInactive"))}<span class="dim"> · IHC ${esc(serial)}</span></div>`).join("") : `<span class="dim">${esc(this.t("setNoController"))}</span>`}</div>
        <details class="help"><summary>${esc(this.t("setWhy"))}</summary><p>${esc(this.t("setWhyText"))}</p></details>
        ${st.error ? `<p class="ferr box">${esc(st.error)}</p>` : ""}
        <div class="formfoot"><span class="grow"></span><button class="btn small" data-act="save-settings" ${st.busy ? "disabled" : ""}>${esc(st.busy ? this.t("saving") : this.t("save"))}</button></div>
      </section></div>`;
    body.querySelectorAll("[data-setf]").forEach((el) => el.addEventListener("change", () => {
      f[el.dataset.setf] = el.type === "checkbox" ? el.checked : el.value;
      if (el.type === "checkbox") this._renderBody();
    }));
  }

  // ------------------------------------------------------------------ reports (like the controller's own report pages)

  async _loadReport() {
    const r = this._rep || (this._rep = { kind: "installation", onlyMarked: true });
    r.loading = true; r.error = ""; if (this._tab === "reports") this._renderBody();
    try { r.data = await this._ws({ type: "viewmyihc/report", report: r.kind, only_marked: r.onlyMarked }); r.dataKind = r.kind; }
    catch (e) { r.error = this._errText(e); r.data = null; }
    r.loading = false;
    if (this._tab === "reports") this._renderBody();
  }

  _renderReports(body) {
    const r = this._rep || {};
    const kinds = ["installation", "function", "functionblocks"].map((k) =>
      `<button class="repkind ${r.kind === k ? "sel" : ""}" data-repkind="${k}"><ha-icon icon="${REPORT_ICON[k]}"></ha-icon>
        <span><b>${esc(this.t("rep_" + k))}</b><small>${esc(this.t("rep_" + k + "_lead"))}</small></span></button>`).join("");
    const ready = r.data && r.dataKind === r.kind && !r.loading;
    body.innerHTML = `<div class="tools reports">
      <section class="card acard"><div class="repkinds">${kinds}</div>
        ${r.kind === "function" ? `<label class="switchrow"><input type="checkbox" data-act="rep-marked" ${r.onlyMarked ? "checked" : ""}/><span>${esc(this.t("repOnlyMarked"))}</span></label>` : ""}
        <div class="formfoot"><span class="dim small">${esc(this.t("repLead"))}</span><span class="grow"></span>
          <button class="btn-text" data-act="rep-download" ${ready ? "" : "disabled"}><ha-icon icon="mdi:download"></ha-icon>${esc(this.t("repDownload"))}</button>
          <button class="btn small" data-act="rep-print" ${ready ? "" : "disabled"}><ha-icon icon="mdi:printer-outline"></ha-icon> ${esc(this.t("repPrint"))}</button></div>
      </section>
      ${r.error ? this._toolError(r.error, "rep-reload") : !ready ? `<div class="state"><div class="spinner"></div></div>`
        : `<div class="paper">${this._reportHtml(r.dataKind, r.data)}</div>`}</div>`;
  }

  // The report as plain HTML: the same markup is shown in the panel, printed and downloaded.
  _reportHtml(kind, d) {
    const doc = d.documentation || {}, info = d.info || {};
    const v = (x) => esc(x ?? "") || "&nbsp;";
    const table = (cols, rows) => `<table class="rt"><thead><tr>${cols.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${rows.join("")}</tbody></table>`;
    const kv = (pairs) => `<table class="rkv">${pairs.filter(([, x]) => x).map(([k, x]) => `<tr><th>${esc(k)}</th><td>${esc(x)}</td></tr>`).join("")}</table>`;
    const person = (p) => p ? kv([[this.t("name"), p.name], [this.t("repAddress"), [p.address, [p.zipcode, p.city].filter(Boolean).join(" "), p.country].filter(Boolean).join(", ")],
      [this.t("phone"), [p.phone, p.mobilephone].filter(Boolean).join(" / ")], [this.t("email"), p.email]]) : "";
    const generated = new Date().toLocaleString(this._hass?.language || undefined, { dateStyle: "long", timeStyle: "short" });
    const head = `<header class="rhead"><h1>${esc(this.t("rep_" + kind))}</h1>
      <div class="rsub">${esc(info.description || doc.project?.description || "")}${info.modified ? ` · ${esc(this.t("modified"))} ${esc(info.modified)}` : ""} · ${esc(this.t("repGenerated").replace("{time}", generated))}</div></header>`;
    const val = (x, kindName) => esc(x === "on" ? this.t("on") : x === "off" ? this.t("off") : kindName === "weekday" ? this.tk("weekdays", x) : x);
    if (kind === "installation") {
      const io = (rows, what) => table([this.t("repTerminal"), this.t("repProduct"), what, this.t("note"), this.t("repLocation"), this.t("repPosition"),
        this.t("repTag"), this.t("repCableType"), this.t("repCableNo"), this.t("repPowerGroup"), this.t("repColour")],
        rows.map((r) => `<tr><td class="mono">${v(r.terminal)}</td><td>${v(r.product)}</td><td>${v(r.name)}</td><td>${v(r.note)}</td><td>${v(r.location)}</td>
          <td>${v(r.position)}</td><td>${v(r.tag)}</td><td>${v(r.cabletype)}</td><td>${v(r.cablenumber)}</td><td>${v(r.power_group)}</td><td>${v(r.colour)}</td></tr>`));
      const modules = (list) => list.length ? table([this.t("repLine"), this.t("repModuleType"), this.t("repLocation")],
        list.map((m) => `<tr><td>${m.line}</td><td>${v(m.type)}</td><td>${v(m.location)}</td></tr>`)) : `<p class="rpos">${esc(this.t("repNoModules"))}</p>`;
      const products = d.products.map((p) => `<div class="rprod">${kv([[this.t("repLocation"), p.location], [this.t("repPosition"), p.position],
        [this.t("repComponent"), p.name], [this.t("repTag"), p.tag], [this.t("repCableNo"), p.cablenumber], [this.t("repCableType"), p.cabletype],
        [this.t("repPowerGroup"), p.power_group], [this.t("repSerial"), p.serial]])}
        ${p.terminals.length ? table([this.t("repTerminal"), this.t("repColour"), this.t("repIn"), this.t("repOut")], p.terminals.map((t) =>
          `<tr><td class="mono">${v(t.terminal || t.channel)}</td><td>${v(t.colour)}</td><td>${t.direction === "in" ? v(t.name) : "&nbsp;"}</td><td>${t.direction === "out" ? v(t.name) : "&nbsp;"}</td></tr>`)) : ""}</div>`).join("");
      return `${head}
        <section class="rsec two">${doc.customer ? `<div><h2>${esc(this.t("repCustomer"))}</h2>${person(doc.customer)}</div>` : ""}
          ${doc.installer ? `<div><h2>${esc(this.t("repInstaller"))}</h2>${person(doc.installer)}</div>` : ""}</section>
        <section class="rsec"><h2>${esc(this.t("dlInputs"))}</h2>${io(d.inputs, this.t("repIn"))}</section>
        <section class="rsec"><h2>${esc(this.t("dlOutputs"))}</h2>${io(d.outputs, this.t("repOut"))}</section>
        <section class="rsec two"><div><h2>${esc(this.t("repInModules"))}</h2>${modules(d.input_modules)}</div><div><h2>${esc(this.t("repOutModules"))}</h2>${modules(d.output_modules)}</div></section>
        <section class="rsec"><h2>${esc(this.t("repProducts"))}</h2><div class="rprods">${products}</div></section>`;
    }
    if (kind === "function") {
      if (!d.groups.length) return `${head}<p>${esc(this.t(d.marked_any ? "repNone" : "repNoneMarked"))}</p>`;
      return `${head}${d.groups.map((g) => `<section class="rsec rgroup"><h2>${esc(g.name)}</h2>${g.products.map((p) => `<div class="rbutton">
        <h3>${esc(p.name)}${p.position ? ` <span class="rpos">${esc(p.position)}</span>` : ""}</h3>
        ${p.inputs.map((i) => `<div class="rin"><b>${esc(i.name)}</b>${i.does.length ? `<ul>${i.does.map((x) => `<li>${esc(x.text)}${x.where ? ` <span class="rpos">(${esc(x.where)})</span>` : ""}</li>`).join("")}</ul>`
          : `<span class="rpos"> – ${esc(this.t("repNotUsed"))}</span>`}</div>`).join("")}
        ${p.outputs.length ? `<div class="rout">${esc(this.t("repOutputs"))}: ${p.outputs.map((o) => esc(o.name + (o.note ? ` (${o.note})` : ""))).join(", ")}</div>` : ""}</div>`).join("")}</section>`).join("")}`;
    }
    return `${head}${d.blocks.map((b) => `<section class="rsec rblock"><h2>${esc(b.name)} <span class="rpos">${esc(b.location)}</span></h2>
      ${b.note ? `<p class="rnote">${esc(b.note)}</p>` : ""}
      ${b.sections.map((s) => `<h3>${esc(s.title)}</h3>${table([this.t("name"), this.t("repType"), this.t("repInitial"), this.t("note"), this.t("links")],
        s.resources.map((r) => `<tr><td>${v(r.name)}</td><td>${esc(this.tk("kind", r.kind))}</td><td>${val(r.initial, r.kind) || "&nbsp;"}</td><td>${v(r.note)}</td>
          <td>${r.links.map((l) => esc(l.label)).join("<br>") || "&nbsp;"}</td></tr>`))}`).join("")}</section>`).join("")}`;
  }

  _reportDocument() {
    const r = this._rep;
    return `<!doctype html><html lang="${this._lang}"><head><meta charset="utf-8"><title>${esc(this.t("rep_" + r.dataKind))} – ${esc(r.data.info?.description || "IHC")}</title>
      <style>${REPORT_CSS}</style></head><body><div class="paper">${this._reportHtml(r.dataKind, r.data)}</div></body></html>`;
  }

  _reportPrint() {
    const w = window.open("", "_blank");
    if (!w) { this._showToast(this.t("repPopup")); return; }
    w.document.open(); w.document.write(this._reportDocument()); w.document.close();
    w.focus();
    setTimeout(() => w.print(), 300);  // let the new window lay the report out first
  }

  _reportDownload() {
    const r = this._rep;
    const name = `${this.t("rep_" + r.dataKind)}-${(r.data.info?.description || "ihc").replace(/[^\wæøåÆØÅ-]+/g, "_")}-${new Date().toISOString().slice(0, 10)}.html`;
    this._downloadBlob(new Blob([this._reportDocument()], { type: "text/html" }), name);
  }

  // ------------------------------------------------------------------ wiring map
  // Controller in the middle, input modules to the left and output modules to the right, each wire leaving the
  // module at the terminal it is really connected to. Drawn as SVG; pan/zoom by changing the viewBox.

  async _loadMap() {
    const m = this._map || (this._map = { view: null, sel: null, q: "", images: {} });
    m.loading = true; m.error = ""; if (this._tab === "map") this._renderBody();
    try {
      m.data = await this._ws({ type: "viewmyihc/map" });
      m.layout = this._mapLayout(m.data);
    } catch (e) { m.error = this._errText(e); }
    m.loading = false;
    if (this._tab === "map") this._renderBody();
    if (m.data) this._loadMapImages();
  }

  async _loadMapImages() {
    const m = this._map;
    const ids = [...new Set(m.data.products.map((p) => p.identifier).filter((id) => id && !(id in m.images)))];
    if (!ids.length) return;
    try {
      const res = await this._ws({ type: "viewmyihc/map/images", identifiers: ids });
      Object.assign(m.images, res.images);
      if (this._tab === "map") this._drawMap();
    } catch (_e) { /* the drawn icons stay */ }
  }

  _mapLayout(d) {
    const C = MAP;
    const nodes = { modules: [], products: [], wires: [], cables: [] };
    const sides = { inputs: -1, outputs: 1 };
    const side_modules = {};
    for (const [side, dir] of Object.entries(sides)) {
      const list = d[side].map((l) => ({ key: `${side}:${l.line}`, side, line: l.line, type: l.type, location: l.location,
        capacity: l.capacity, used: l.used - l.outside, outside: l.outside, slots: l.slots }));
      const air = d.airlink[side];
      if (air.length) {
        list.push({ key: `${side}:air`, side, air: true, line: null, type: this.t("mapAirlink"), location: "", capacity: air.length,
          used: air.length, outside: 0, slots: air.map((a, i) => ({ position: i + 1, usable: true, ...a, terminal: `CH${parseInt(a.channel, 16) || i + 1}` })) });
      }
      side_modules[side] = list;
    }
    const productById = new Map(d.products.map((p) => [p.id, p]));
    let colorIndex = 0;
    for (const [side, dir] of Object.entries(sides)) {
      const mods = side_modules[side];
      // terminals: first half on top, the rest at the bottom, like on the module itself
      for (const mod of mods) {
        const usable = mod.slots.filter((s) => s.usable), extra = mod.slots.filter((s) => !s.usable);
        const half = Math.ceil(usable.length / 2);
        mod.top = mod.air ? [] : usable.slice(0, half);
        mod.bottom = mod.air ? [] : [...usable.slice(half), ...extra];
        mod.hue = mod.air ? null : (colorIndex++ * 47) % 360;
      }
      // products in the order of the terminals they hang on; a product appears once per side
      const placed = new Map();
      const wiresBySide = [];
      for (const mod of mods) {
        mod.products = [];
        const order = mod.air ? mod.slots : [...mod.top, ...mod.bottom];
        for (const slot of order) {
          if (!slot.name || !productById.has(slot.product_id)) continue;
          if (!placed.has(slot.product_id)) {
            const p = { ...productById.get(slot.product_id), key: `${side}:${slot.product_id}`, side, ports: [] };
            placed.set(slot.product_id, p); mod.products.push(p);
          }
          wiresBySide.push({ mod, slot, product: placed.get(slot.product_id) });
        }
      }
      for (const w of wiresBySide) w.product.ports.push(w);
      // vertical layout: each module with its products forms a block; blocks are stacked and centred on the controller
      let y = 0;
      for (const mod of mods) {
        for (const p of mod.products) p.h = Math.max(C.prodH, 30 + p.ports.length * C.portGap);
        const n = mod.products.length;
        mod.cols = n <= 3 ? 1 : n <= 8 ? 2 : n <= 15 ? 3 : 4;
        mod.rows = Math.max(1, Math.ceil(n / mod.cols));
        mod.rowH = Math.max(C.prodH, ...mod.products.map((p) => p.h)) + C.prodGap;
        mod.blockH = Math.max(C.modH + 2 * C.modRoom, mod.rows * mod.rowH - C.prodGap);
        mod.blockY = y;
        y += mod.blockH + C.blockGap;
      }
      const total = Math.max(y - C.blockGap, 0), offset = -total / 2;
      const modX = dir < 0 ? -C.ctrlW / 2 - C.gapCM - C.modW : C.ctrlW / 2 + C.gapCM;
      const prodX = dir < 0 ? modX - C.gapMP - C.prodW : modX + C.modW + C.gapMP;
      for (const mod of mods) {
        mod.x = modX; mod.y = offset + mod.blockY + mod.blockH / 2 - C.modH / 2; mod.w = C.modW; mod.h = C.modH;
        const rowX = (row, i) => mod.x + 26 + (row.length > 1 ? i * (C.modW - 52) / (row.length - 1) : (C.modW - 52) / 2);
        mod.top.forEach((s, i) => { s.x = rowX(mod.top, i); s.y = mod.y; s.row = "top"; });
        mod.bottom.forEach((s, i) => { s.x = rowX(mod.bottom, i); s.y = mod.y + C.modH; s.row = "bottom"; });
        // column by column, the one nearest the module first, each in terminal order
        const top = offset + mod.blockY + (mod.blockH - (mod.rows * mod.rowH - C.prodGap)) / 2;
        mod.products.forEach((p, i) => {
          const row = i % mod.rows, col = Math.floor(i / mod.rows);
          p.x = prodX + dir * col * (C.prodW + C.colGap); p.y = top + row * mod.rowH; p.w = C.prodW;
          p.ports.forEach((w, k) => {
            w.px = dir < 0 ? p.x + p.w : p.x;
            w.py = p.y + (p.h / (p.ports.length + 1)) * (k + 1);
          });
          nodes.products.push(p);
        });
        nodes.modules.push(mod);
      }
      for (const w of wiresBySide) {
        const { mod, slot } = w;
        const sx = mod.air ? (dir < 0 ? mod.x : mod.x + mod.w) : slot.x;
        const sy = mod.air ? mod.y + mod.h / 2 : slot.y;
        const out = mod.air ? 0 : slot.row === "top" ? -1 : 1;
        const lead = 46 + (slot.position % 8) * 3;
        const c1 = mod.air ? [sx + dir * 140, sy] : [sx, sy + out * lead];
        const c2 = [w.px - dir * 150, w.py];
        nodes.wires.push({ d: `M${sx},${sy} C${c1[0]},${c1[1]} ${c2[0]},${c2[1]} ${w.px},${w.py}`, hue: mod.hue, air: !!mod.air,
          mod: mod.key, product: w.product.key, pid: w.product.id, rid: slot.id, sx, sy });
      }
    }
    // the controller: one port per module on each side
    const ports = Math.max(side_modules.inputs.length, side_modules.outputs.length, 4);
    const ctrl = { x: -C.ctrlW / 2, w: C.ctrlW, h: Math.max(C.ctrlH, ports * 34 + 120) };
    ctrl.y = -ctrl.h / 2;
    for (const [side, dir] of Object.entries(sides)) {
      const mods = side_modules[side];
      mods.forEach((mod, i) => {
        const px = dir < 0 ? ctrl.x : ctrl.x + ctrl.w;
        const py = ctrl.y + 90 + (ctrl.h - 120) * (mods.length > 1 ? i / (mods.length - 1) : 0.5);
        const mx = dir < 0 ? mod.x + mod.w : mod.x, my = mod.y + mod.h / 2;
        nodes.cables.push({ d: `M${px},${py} C${px + dir * 120},${py} ${mx - dir * 120},${my} ${mx},${my}`, hue: mod.hue, air: !!mod.air,
          mod: mod.key, px, py, label: mod.air ? "RF" : String(mod.line) });
      });
    }
    nodes.ctrl = ctrl;
    const xs = [...nodes.products.map((p) => [p.x, p.x + p.w]).flat(), ...nodes.modules.map((m) => [m.x, m.x + m.w]).flat(), ctrl.x, ctrl.x + ctrl.w];
    const ys = [...nodes.products.map((p) => [p.y, p.y + p.h]).flat(), ...nodes.modules.map((m) => [m.y - 80, m.y + m.h + 80]).flat(), ctrl.y, ctrl.y + ctrl.h];
    nodes.bounds = { x: Math.min(...xs) - 60, y: Math.min(...ys) - 60, w: Math.max(...xs) - Math.min(...xs) + 120, h: Math.max(...ys) - Math.min(...ys) + 120 };
    const homeW = C.ctrlW + 2 * (C.gapCM + C.modW) + 240;
    nodes.home = { x: -homeW / 2, y: Math.min(ctrl.y - 80, -homeW * 0.3), w: homeW, h: Math.max(ctrl.h + 160, homeW * 0.6) };
    return nodes;
  }

  _mapIcon(p) {
    return PRODUCT_ICON[p.identifier] || (p.kind === "product_airlink" ? "mdi:remote" : p.side === "inputs" ? "mdi:gesture-tap-button" : "mdi:power-plug-outline");
  }

  _renderMap(body) {
    const m = this._map;
    if (!m || m.loading && !m.layout) { body.innerHTML = `<div class="state"><div class="spinner"></div></div>`; return; }
    if (m.error) { body.innerHTML = this._toolError(m.error, "map-reload"); return; }
    const unwired = m.data.unwired.length;
    body.innerHTML = `<div class="mapwrap">
      <div class="maptools">
        <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input type="search" data-mapq placeholder="${esc(this.t("mapSearch"))}" value="${esc(m.q)}"/></label>
        <span class="mapfound dim small"></span><span class="grow"></span>
        ${unwired ? `<span class="dim small mapnote">${esc(this.t("mapUnwired").replace("{n}", unwired))}</span>` : ""}
        <button class="icon-btn" data-act="map-zoom" data-f="1.4" title="${esc(this.t("mapZoomIn"))}"><ha-icon icon="mdi:magnify-plus-outline"></ha-icon></button>
        <button class="icon-btn" data-act="map-zoom" data-f="0.7" title="${esc(this.t("mapZoomOut"))}"><ha-icon icon="mdi:magnify-minus-outline"></ha-icon></button>
        <button class="icon-btn" data-act="map-home" title="${esc(this.t("mapHome"))}"><ha-icon icon="mdi:target"></ha-icon></button>
        <button class="icon-btn" data-act="map-all" title="${esc(this.t("mapAll"))}"><ha-icon icon="mdi:fit-to-screen-outline"></ha-icon></button>
      </div>
      <div class="mapstage"><svg class="mapsvg" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet"></svg>
        <div class="mapcard" hidden></div></div></div>`;
    const input = body.querySelector("[data-mapq]");
    input.addEventListener("input", (e) => { m.q = e.target.value; this._mapSearch(false); });
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); this._mapSearch(true); } });
    this._mapBind(body.querySelector(".mapsvg"));
    this._drawMap();
    if (!m.view) this._mapFit("home"); else this._mapApply();
    this._renderMapCard();
  }

  _drawMap() {
    const svg = this.shadowRoot.querySelector(".mapsvg"); const m = this._map; if (!svg || !m?.layout) return;
    const L = m.layout, C = MAP;
    const wireColor = (w, light) => (w.hue === null || w.hue === undefined ? "var(--vmi-sub)" : `hsl(${w.hue} 60% ${light ? 50 : 42}%)`);
    const trunc = (s, n) => (s && s.length > n ? s.slice(0, n - 1) + "…" : s || "");
    const label = (pos) => (pos > 8 ? pos + 2 : "0" + pos);
    const parts = [];
    parts.push(`<g class="cables">${L.cables.map((c) => `<path class="cable ${c.air ? "air" : ""}" data-m="${c.mod}" d="${c.d}" stroke="${wireColor(c)}"/>`).join("")}</g>`);
    parts.push(`<g class="wires">${L.wires.map((w) => `<path class="wire ${w.air ? "air" : ""}" data-m="${w.mod}" data-p="${w.product}" d="${w.d}" stroke="${wireColor(w, true)}"/>`).join("")}</g>`);
    const ct = L.ctrl;
    parts.push(`<g class="ctrl" data-act="map-ctrl"><rect x="${ct.x}" y="${ct.y}" width="${ct.w}" height="${ct.h}" rx="14"/>
      <rect class="ctrl-top" x="${ct.x}" y="${ct.y}" width="${ct.w}" height="64" rx="14"/><rect class="ctrl-top" x="${ct.x}" y="${ct.y + 40}" width="${ct.w}" height="24"/>
      <text class="t-big" x="0" y="${ct.y + 30}" text-anchor="middle">IHC Controller</text>
      <text class="t-sub on-dark" x="0" y="${ct.y + 52}" text-anchor="middle">${esc(m.data.serial || "")}</text>
      <text class="t-sub" x="0" y="${ct.y + ct.h - 18}" text-anchor="middle">${esc(trunc(m.data.info?.description || "", 26))}</text>
      <text class="t-sub" x="${ct.x + 14}" y="${ct.y + 92}">${esc(this.t("mapIn"))}</text>
      <text class="t-sub" x="${ct.x + ct.w - 14}" y="${ct.y + 92}" text-anchor="end">${esc(this.t("mapOut"))}</text>
      ${L.cables.map((c) => `<circle class="cport" cx="${c.px}" cy="${c.py}" r="7" fill="${wireColor(c)}"/><text class="t-port" x="${c.px + (c.px < 0 ? 14 : -14)}" y="${c.py + 4}" text-anchor="${c.px < 0 ? "start" : "end"}">${esc(c.label)}</text>`).join("")}</g>`);
    for (const mod of L.modules) {
      const term = (s) => `<g class="term ${s.name ? "used" : ""} ${s.usable ? "" : "outside"}">
          <circle cx="${s.x}" cy="${s.y}" r="6" ${s.name ? `fill="${wireColor(mod, true)}"` : ""}/>
          <text class="t-term lod1" x="${s.x}" y="${s.row === "top" ? s.y + 20 : s.y - 12}" text-anchor="middle">${label(s.position)}</text></g>`;
      parts.push(`<g class="mod ${mod.air ? "air" : ""}" data-act="map-mod" data-key="${mod.key}">
        <rect x="${mod.x}" y="${mod.y}" width="${mod.w}" height="${mod.h}" rx="8" style="--hue:${mod.hue ?? 0}"/>
        <rect class="mod-band" x="${mod.x}" y="${mod.y + mod.h / 2 - 22}" width="${mod.w}" height="44" ${mod.hue !== null ? `fill="hsl(${mod.hue} 55% 45% / .14)"` : ""}/>
        <text class="t-mod" x="${mod.x + mod.w / 2}" y="${mod.y + mod.h / 2 - 3}" text-anchor="middle">${esc(mod.air ? mod.type : `${this.t("dlLine").replace("{n}", mod.line)} · ${mod.type || this.t("mapNoModule")}`)}</text>
        <text class="t-sub lod1" x="${mod.x + mod.w / 2}" y="${mod.y + mod.h / 2 + 16}" text-anchor="middle">${esc([mod.location, `${mod.used}/${mod.capacity}`].filter(Boolean).join(" · "))}</text>
        ${mod.air ? `<foreignObject x="${mod.x + 10}" y="${mod.y + mod.h / 2 - 16}" width="32" height="32"><ha-icon icon="mdi:access-point" style="color:var(--vmi-accent)"></ha-icon></foreignObject>` : ""}
        ${[...mod.top, ...mod.bottom].map(term).join("")}</g>`);
    }
    for (const p of L.products) {
      const img = m.images[p.identifier];
      const ix = p.x + 10, iy = p.y + p.h / 2 - 26;
      parts.push(`<g class="prod" data-act="map-prod" data-key="${p.key}" data-p="${p.key}">
        <rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="10"/>
        <rect class="imgbg" x="${ix - 2}" y="${iy - 2}" width="56" height="56" rx="6"/>
        ${img ? `<image href="${img}" x="${ix}" y="${iy}" width="52" height="52" preserveAspectRatio="xMidYMid meet"/>`
          : `<foreignObject x="${ix + 8}" y="${iy + 8}" width="36" height="36"><ha-icon icon="${this._mapIcon(p)}" style="--mdc-icon-size:36px;color:var(--vmi-accent)"></ha-icon></foreignObject>`}
        <text class="t-prod" x="${ix + 64}" y="${p.y + p.h / 2 - 6}">${esc(trunc(p.name, 24))}</text>
        <text class="t-sub lod1" x="${ix + 64}" y="${p.y + p.h / 2 + 12}">${esc(trunc([p.location, p.position].filter(Boolean).join(" · "), 30))}</text>
        <title>${esc([p.name, p.location, p.position].filter(Boolean).join(" · "))}</title>
        ${p.ports.map((w) => `<circle class="pport" cx="${w.px}" cy="${w.py}" r="4" fill="${wireColor(w.mod, true)}"/>`).join("")}</g>`);
    }
    svg.innerHTML = parts.join("");
    this._mapHighlight();
  }

  // ---- view: pan and zoom by changing the viewBox

  _mapStage() { return this.shadowRoot.querySelector(".mapsvg"); }

  _mapFit(what) {
    const m = this._map, svg = this._mapStage(); if (!svg || !m?.layout) return;
    const box = what === "all" ? m.layout.bounds : m.layout.home;
    const r = svg.getBoundingClientRect(), aspect = (r.width || 800) / (r.height || 600);
    let { x, y, w, h } = box;
    if (w / h > aspect) { const nh = w / aspect; y -= (nh - h) / 2; h = nh; } else { const nw = h * aspect; x -= (nw - w) / 2; w = nw; }
    m.view = { x, y, w, h };
    this._mapApply();
  }

  _mapApply() {
    const m = this._map, svg = this._mapStage(); if (!svg || !m?.view) return;
    const v = m.view;
    svg.setAttribute("viewBox", `${v.x} ${v.y} ${v.w} ${v.h}`);
    const scale = (svg.getBoundingClientRect().width || 800) / v.w;
    svg.dataset.lod = scale < 0.22 ? "far" : scale < 0.45 ? "mid" : "near";
  }

  // zoom by `factor` around a point given in screen pixels (the centre when not given)
  _mapZoom(factor, clientX, clientY) {
    const m = this._map, svg = this._mapStage(); if (!svg || !m?.view) return;
    const r = svg.getBoundingClientRect(), v = m.view;
    const fx = clientX === undefined ? 0.5 : (clientX - r.left) / r.width, fy = clientY === undefined ? 0.5 : (clientY - r.top) / r.height;
    const b = m.layout.bounds;
    const w = Math.min(Math.max(v.w / factor, 220), Math.max(b.w, b.h * (r.width / r.height)) * 2.5);
    const h = w * (v.h / v.w);
    m.view = { x: v.x + (v.w - w) * fx, y: v.y + (v.h - h) * fy, w, h };
    this._mapApply();
  }

  _mapBind(svg) {
    const pts = new Map();
    let last = null, moved = 0, frame = 0;
    const flush = () => { frame = 0; this._mapApply(); };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(flush); };
    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const m = this._map; if (!m?.view) return;
      const factor = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015));
      this._mapZoom(factor, e.clientX, e.clientY);
    }, { passive: false });
    svg.addEventListener("pointerdown", (e) => {
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size === 1) moved = 0;
      last = null;
    });
    svg.addEventListener("pointermove", (e) => {
      if (!pts.has(e.pointerId)) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      const m = this._map; if (!m?.view) return;
      const list = [...pts.values()];
      const r = svg.getBoundingClientRect(), scale = r.width / m.view.w;
      const cur = list.length >= 2
        ? { x: (list[0].x + list[1].x) / 2, y: (list[0].y + list[1].y) / 2, d: Math.hypot(list[0].x - list[1].x, list[0].y - list[1].y), n: 2 }
        : { x: list[0].x, y: list[0].y, d: 0, n: 1 };
      if (last && last.n === cur.n) {
        const dx = cur.x - last.x, dy = cur.y - last.y;
        moved += Math.abs(dx) + Math.abs(dy);
        // only a real drag takes the pointer: a plain click must still reach the product or module under it
        if (moved > 6 && !svg.hasPointerCapture(e.pointerId)) { try { svg.setPointerCapture(e.pointerId); } catch (_e) { /* gone */ } }
        m.view.x -= dx / scale; m.view.y -= dy / scale;
        if (cur.n === 2 && last.d > 0 && cur.d > 0) { this._mapZoom(cur.d / last.d, cur.x, cur.y); moved += 10; }
        schedule();
      }
      last = cur;
    });
    const end = (e) => { pts.delete(e.pointerId); last = null; };
    svg.addEventListener("pointerup", end); svg.addEventListener("pointercancel", end);
    // a drag must not count as a click on whatever is under the pointer
    svg.addEventListener("click", (e) => { if (moved > 6) { e.stopPropagation(); e.preventDefault(); } }, true);
  }

  // ---- selection, highlight, card, search

  _mapSelect(sel) {
    this._map.sel = sel;
    this._mapHighlight();
    this._renderMapCard();
    this._schedule(true);
  }

  _mapHighlight() {
    const svg = this._mapStage(); const sel = this._map?.sel; if (!svg) return;
    svg.classList.toggle("has-sel", !!sel);
    svg.querySelectorAll(".hl").forEach((el) => el.classList.remove("hl"));
    if (!sel) return;
    if (sel.type === "prod") {
      const pid = sel.key.split(":")[1];
      svg.querySelectorAll(`[data-p$=":${pid}"]`).forEach((el) => el.classList.add("hl"));
      const mods = new Set([...svg.querySelectorAll(`.wire[data-p$=":${pid}"]`)].map((el) => el.dataset.m));
      mods.forEach((k) => svg.querySelectorAll(`.mod[data-key="${k}"], .cable[data-m="${k}"]`).forEach((el) => el.classList.add("hl")));
    } else if (sel.type === "mod") {
      svg.querySelectorAll(`[data-m="${sel.key}"], .mod[data-key="${sel.key}"]`).forEach((el) => el.classList.add("hl"));
      const prods = new Set([...svg.querySelectorAll(`.wire[data-m="${sel.key}"]`)].map((el) => el.dataset.p));
      prods.forEach((k) => svg.querySelectorAll(`.prod[data-key="${k}"]`).forEach((el) => el.classList.add("hl")));
    }
    svg.querySelector(".ctrl")?.classList.add("hl");
  }

  _mapCardIds() {
    const m = this._map; if (!m?.sel || m.sel.type !== "prod" || !m.layout) return [];
    const pid = Number(m.sel.key.split(":")[1]);
    return m.layout.wires.filter((w) => w.pid === pid).map((w) => w.rid).filter(Boolean);
  }

  _renderMapCard() {
    const el = this.shadowRoot.querySelector(".mapcard"); const m = this._map; if (!el) return;
    const sel = m?.sel; el.hidden = !sel; if (!sel) { el.innerHTML = ""; return; }
    const L = m.layout, label = (pos) => (pos > 8 ? pos + 2 : "0" + pos);
    let html = "";
    if (sel.type === "prod") {
      const pid = Number(sel.key.split(":")[1]);
      const p = L.products.find((x) => x.id === pid);
      const rows = L.modules.flatMap((mod) => mod.slots.filter((s) => s.product_id === pid && s.name).map((s) => ({ mod, s })));
      const img = m.images[p.identifier];
      html = `<header>${img ? `<img src="${img}" alt=""/>` : `<ha-icon icon="${this._mapIcon(p)}"></ha-icon>`}
          <div><h3>${esc(p.name)}</h3><div class="dim small">${esc([p.location, p.position].filter(Boolean).join(" · "))}</div></div>
          <button class="icon-btn" data-act="map-close" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button></header>
        <ul class="maprows">${rows.map(({ mod, s }) => {
          const f = this._values.has(s.id) ? this.fmt(s.kind, this._values.get(s.id)) : { text: "", cls: "none" };
          const place = mod.air ? s.terminal : `${mod.side === "inputs" ? "I" : "O"}${mod.line}.${label(s.position)}`;
          return `<li><code>${esc(place)}</code><span class="grow">${esc(s.name)}</span>
            <span class="val ${f.cls}" data-val="${s.id}" data-kind="${esc(s.kind || "bool")}">${esc(f.text)}</span>
            <button class="icon-btn tiny" data-jump="${s.id}" title="${esc(this.t("showInTree"))}"><ha-icon icon="mdi:file-tree"></ha-icon></button></li>`;
        }).join("")}</ul>`;
    } else if (sel.type === "mod") {
      const mod = L.modules.find((x) => x.key === sel.key);
      html = `<header><ha-icon icon="${mod.air ? "mdi:access-point" : "mdi:expansion-card-variant"}"></ha-icon>
          <div><h3>${esc(mod.air ? mod.type : `${this.t("dlLine").replace("{n}", mod.line)} · ${mod.type || this.t("mapNoModule")}`)}</h3>
          <div class="dim small">${esc([mod.location, this.t("dlUsed").replace("{used}", mod.used).replace("{all}", mod.capacity)].filter(Boolean).join(" · "))}</div></div>
          <button class="icon-btn" data-act="map-close" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button></header>
        <ul class="maprows">${mod.products.map((p) => `<li><button class="linkbtn" data-act="map-prod" data-key="${p.key}">${esc(p.name)}</button>
          <span class="dim small grow">${esc(p.location)}</span></li>`).join("") || `<li class="dim">${esc(this.t("empty"))}</li>`}</ul>`;
    } else {
      const d = m.data;
      const count = (side) => d[side].reduce((n, l) => n + l.used - l.outside, 0);
      html = `<header><ha-icon icon="mdi:server-network"></ha-icon><div><h3>IHC Controller</h3><div class="dim small">${esc(d.serial || "")}</div></div>
          <button class="icon-btn" data-act="map-close" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button></header>
        <ul class="maprows"><li><span class="grow">${esc(this.t("dlInputs"))}</span><b>${count("inputs")}</b> · ${d.inputs.length} ${esc(this.t("mapLines"))}</li>
          <li><span class="grow">${esc(this.t("dlOutputs"))}</span><b>${count("outputs")}</b> · ${d.outputs.length} ${esc(this.t("mapLines"))}</li>
          <li><span class="grow">${esc(this.t("products"))}</span><b>${d.products.length}</b></li></ul>`;
    }
    el.innerHTML = html;
    this._paintValues();
  }

  _mapSearch(next) {
    const m = this._map, q = (m.q || "").trim().toLowerCase(), info = this.shadowRoot.querySelector(".mapfound");
    if (!q) { if (info) info.textContent = ""; return; }
    const hits = m.layout.products.filter((p) => `${p.name} ${p.location} ${p.position}`.toLowerCase().includes(q));
    if (info) info.textContent = hits.length ? this.t("mapHits").replace("{n}", hits.length) : this.t("noResults");
    if (!hits.length) return;
    m.hit = next ? ((m.hit ?? -1) + 1) % hits.length : 0;
    this._mapFocus(hits[m.hit]);
  }

  _mapFocus(p) {
    const m = this._map, svg = this._mapStage(); if (!svg) return;
    const r = svg.getBoundingClientRect(), w = Math.max(900, p.w * 3.5), h = w * (r.height / r.width);
    m.view = { x: p.x + p.w / 2 - w / 2, y: p.y + p.h / 2 - h / 2, w, h };
    this._mapApply();
    this._mapSelect({ type: "prod", key: p.key });
  }

  _switchTab(tab) {
    if (tab === this._tab) return;
    if (tab === "admin") { this._openAdmin(); return; }
    this._tab = tab; this._renderTabs(); this._renderBody();
    if (tab === "entities") { this._loadEntityRows(); this._runCheck(); this._loadCoverage(); }
    else if (tab === "modules") {
      if (!this._dl || this._dl.error) this._loadDataline();
      else { this._schedule(true); if (Date.now() - (this._dl.checked || 0) > ADMIN_RECHECK_MS) this._refreshDataline(); }
    }
    else if (tab === "log") this._openLog();
    else if (tab === "versions") this._loadBackups();
    else if (tab === "settings") this._loadSettings();
    else if (tab === "reports") { if (!this._rep?.data) this._loadReport(); }
    else if (tab === "map") { if (!this._map?.layout) this._loadMap(); else this._schedule(true); }
    else { this._schedule(true); this._loadExisting(); }
  }

  async _loadEntityRows() {
    try { this._entityRows = (await this._ws({ type: "viewmyihc/entity/list" })).entities; this._entityError = ""; }
    catch (e) { this._entityRows = null; this._entityError = (e && (e.message || e.code)) || String(e); }
    if (this._tab === "entities") this._renderBody();
  }

  _stateOf(entityId) {
    const s = entityId && this._hass?.states?.[entityId];
    if (!s) return null;
    const unit = s.attributes?.unit_of_measurement;
    return { text: unit ? `${s.state} ${unit}` : s.state, raw: s.state };
  }

  _entityRowHtml(r) {
    const st = this._stateOf(r.entity_id);
    const area = r.area_id && this._hass?.areas?.[r.area_id]?.name;
    return `<div class="erow" data-ihc="${r.ihc_id}">
      <ha-icon class="eico" icon="${PLATFORM_ICON[r.platform]}"></ha-icon>
      <div class="einfo">
        <div class="ename">${esc(r.name)}</div>
        <div class="esub">${[
          r.entity_id ? `<button class="linkbtn" data-act="more-info" data-entity="${esc(r.entity_id)}">${esc(r.entity_id)}</button>` : "",
          esc(this.tk("platform", r.platform)),
          area ? esc(area) : "",
          r.source === "yaml" ? esc(this.t("inYaml").replace("{file}", r.file).replace("{line}", r.line)) : "",
        ].filter(Boolean).join(" · ")}</div>
      </div>
      ${r.disabled ? `<span class="chip">${esc(this.t("disabledTag"))}</span>` : ""}
      ${r.source === "yaml" ? `<span class="chip wait">${esc(this.t("pending"))}</span>` : `<span class="chip est ${st ? "ok" : ""}" data-entity="${esc(r.entity_id)}">${st ? esc(st.text) : ""}</span>`}
      <button class="chip id" data-copy="${r.ihc_id}" title="${esc(this.t("copy"))}">${r.ihc_id}</button>
      <button class="icon-btn" data-act="show-in-tree" data-id="${r.ihc_id}" title="${esc(this.t("showInTree"))}"><ha-icon icon="mdi:file-tree"></ha-icon></button>
    </div>`;
  }

  _filteredRows() {
    const f = this._entFilter, q = f.q.trim().toLowerCase();
    return (this._entityRows || []).filter((r) => (!f.platform || r.platform === f.platform)
      && (!q || [r.name, r.entity_id, String(r.ihc_id)].some((x) => String(x || "").toLowerCase().includes(q))));
  }

  _renderEntities(body) {
    if (!this._entityRows) {
      body.innerHTML = this._entityError
        ? `<div class="state card err"><h2>${esc(this.t("errorTitle"))}</h2><p>${esc(this._entityError)}</p><button class="btn" data-act="reload-entities">${esc(this.t("retry"))}</button></div>`
        : `<div class="state"><div class="spinner"></div></div>`;
      return;
    }
    const chips = ["", ...Object.keys(PLATFORM_ICON)].map((p) =>
      `<button class="seg ${this._entFilter.platform === p ? "active" : ""}" data-entfilter="${p}">${esc(p ? this.tk("platform", p) : this.t("allTypes"))}</button>`).join("");
    body.innerHTML = `<div class="entities">
      <section class="card acard">
        <h3>${esc(this.t("entitiesTitle"))}<span class="chip">${this._entityRows.length}</span>
          <button class="btn small right" data-act="reload-entities">${esc(this.t("refreshAdmin"))}</button></h3>
        <p class="help">${esc(this.t("entitiesLead"))}</p>
        <div class="toolbar flat"><div class="segmented" role="group">${chips}</div>
          <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input type="search" data-entsearch placeholder="${esc(this.t("entSearch"))}" value="${esc(this._entFilter.q)}" /></label></div>
        <div class="elist"></div>
      </section>
      ${this._coverageCard()}
      ${this._checkCard()}</div>`;
    this._renderEntityList();
    this._renderCoverage();
    const input = body.querySelector("[data-entsearch]");
    input.addEventListener("input", (e) => { this._entFilter.q = e.target.value; this._renderEntityList(); });
  }

  _renderEntityList() {
    const el = this.shadowRoot.querySelector(".elist"); if (!el) return;
    const rows = this._filteredRows();
    el.innerHTML = rows.length ? rows.map((r) => this._entityRowHtml(r)).join("") : `<p class="no-results">${esc(this.t("entNone"))}</p>`;
  }

  // Entity states change all the time: only the small state labels are updated, at most once a second.
  _paintStates() {
    if (this._tab !== "entities" || this._paintedAt > Date.now() - 1000) return;
    this._paintedAt = Date.now();
    this.shadowRoot.querySelectorAll(".chip.est[data-entity]").forEach((el) => {
      const st = this._stateOf(el.dataset.entity);
      el.textContent = st ? st.text : "";
      el.classList.toggle("ok", !!st);
    });
  }

  async _showInTree(id) {
    this._tab = "project"; this._renderTabs(); this._renderBody();
    await this._reveal(id);
  }

  _onAction(t, e) {
    const act = t.dataset.act;
    switch (act) {
      case "create-entity": this._openModal(Number(t.dataset.id)); return true;
      case "modal-close": this._closeModal(); return true;
      case "make-yaml": this._createYaml(); return true;
      case "modal-back": if (this._modal) { this._modal.step = "form"; this._renderModal(); } return true;
      case "verify-yaml": this._verifyInserted(); return true;
      case "copy-yaml": this._copy(this._modal?.result?.placement?.text || this._modal?.result?.yaml || ""); return true;
      case "pick-name": this._modalSet("name", t.dataset.value, true); return true;
      case "show-in-tree": this._showInTree(Number(t.dataset.id)); return true;
      case "reload-entities": this._loadEntityRows(); this._loadExisting(); return true;
      case "refresh-admin": this._openAdmin(true); return true;
      case "save-settings": this._saveSettings(); return true;
      case "map-reload": this._loadMap(); return true;
      case "map-zoom": this._mapZoom(Number(t.dataset.f)); return true;
      case "map-home": this._mapFit("home"); return true;
      case "map-all": this._mapFit("all"); return true;
      case "map-prod": this._mapSelect({ type: "prod", key: t.dataset.key }); return true;
      case "map-mod": this._mapSelect({ type: "mod", key: t.dataset.key }); return true;
      case "map-ctrl": this._mapSelect({ type: "ctrl", key: "ctrl" }); return true;
      case "map-close": this._mapSelect(null); return true;
      case "rep-marked": this._rep.onlyMarked = t.checked; this._loadReport(); return true;
      case "rep-reload": this._loadReport(); return true;
      case "rep-print": this._reportPrint(); return true;
      case "rep-download": this._reportDownload(); return true;
      case "reload-settings": this._loadSettings(); return true;
      case "admin-edit": this._adminStart(t.dataset.key); return true;
      case "admin-cancel": this._adminCancel(); return true;
      case "admin-save": this._adminSave(); return true;
      case "admin-clock": this._adminSetClock(); return true;
      case "admin-confirm": if (this._adminEdit) { this._adminEdit.confirm = t.checked; this._renderBody(); } return true;
      case "user-edit": this._userOpen(t.dataset.user); return true;
      case "user-new": this._userOpen(null); return true;
      case "user-back": if (this._adminEdit) { this._adminEdit.user = null; this._adminEdit.error = ""; this._renderBody(); } return true;
      case "user-save": this._userSave(); return true;
      case "user-delete": this._userDelete(t.dataset.user); return true;
      case "dismiss-bar": this._setAdminBar(null); return true;
      case "clear-marks": this._adminMarks = new Map(); this._adminRemoved = new Map(); this._adminUnits = new Map(); this._renderBody(); return true;
      case "more-info":
        this.dispatchEvent(new CustomEvent("hass-more-info", { detail: { entityId: t.dataset.entity }, bubbles: true, composed: true }));
        return true;
      case "run-check": this._runCheck(); return true;
      case "ctl-bool": this._ctlPut(t.dataset.target, t.dataset.value === "true"); return true;
      case "ctl-set": { const info = this._ctl?.[t.dataset.target]; if (info) this._ctlPut(t.dataset.target, this._ctlInput(t.dataset.target, info)); return true; }
      case "ctl-reload": if (this._selected != null) this._loadCtl(this._selected); return true;
      case "reload-dataline": if (this._dl?.data) this._refreshDataline(); else this._loadDataline(); return true;
      case "reload-log": this._loadUserLog(); return true;
      case "log-order": this._logNewest = !this._logNewest; this._renderLogBody(); return true;
      case "log-clear": this._logClear = { what: t.dataset.what, error: "", busy: false }; this._renderLogBody(); this.shadowRoot.querySelector("[data-clearauth]")?.focus(); return true;
      case "log-clear-cancel": this._logClear = null; this._renderLogBody(); return true;
      case "log-clear-go": this._clearLog(); return true;
      case "reload-messages": this._loadMessages(); return true;
      case "scene-reload": this._loadScene(true); return true;
      case "monitor-start": this._monitorStart(); return true;
      case "monitor-pause": this._mon.paused = !this._mon.paused; this._renderLogBody(); if (!this._mon.paused) this._monitorPoll(); return true;
      case "monitor-csv": this._monitorCsv(); return true;
      case "monitor-clear": this._ws({ type: "viewmyihc/monitor/clear" }).catch(() => {}); this._mon.events = []; this._renderLogBody(); return true;
      case "reload-backups": this._loadBackups(); return true;
      case "backup-download": this._downloadBackup(t.dataset.name); return true;
      case "press-make": this._pressMake(); return true;
      case "press-copy": this._copy(this._press?.yaml || ""); return true;
      default: return false;
    }
  }

  // ------------------------------------------------------------------ "Create entity" = make the YAML entry

  async _openModal(id) {
    let suggest;
    try {
      await this._loadExisting();   // current before the type is chosen: existing types cannot be created again
      suggest = await this._ws({ type: "viewmyihc/entity/suggest", ihc_id: id });
    } catch (e) { this._showToast(e.message || e.code); return; }
    const taken = new Set((this._existing.get(id) || []).map((e) => e.platform));
    const wanted = suggest.default_platform || suggest.platforms.find((p) => p.available)?.platform || "switch";
    const chosen = taken.has(wanted) ? (suggest.platforms.find((p) => p.available && !taken.has(p.platform))?.platform || wanted) : wanted;
    const d = suggest.defaults;
    const detail = this._detail && this._detail.id === id
      ? this._detail : await this._ws({ type: "viewmyihc/detail", ihc_id: id }).catch(() => null);
    this._modal = {
      id, suggest, detail, step: "form", busy: false, errors: {}, result: null, verify: null,
      form: { platform: chosen, name: d.name, note: d.note, position: d.position, options: { ...suggest.option_defaults } },
    };
    this._renderModal();
  }

  _closeModal() {
    this._modal = null;
    clearTimeout(this._previewTimer);
    const host = this.shadowRoot.querySelector(".modal-host"); if (host) host.innerHTML = "";
  }

  _modalSet(field, value, rerender = false) {
    const m = this._modal; if (!m) return;
    if (field.startsWith("options.")) m.form.options[field.slice(8)] = value;
    else m.form[field] = value;
    delete m.errors[field];
    if (rerender) this._renderModal();
    else this._previewSoon();
  }

  _entryFromForm() {
    const { form, id } = this._modal;
    const o = form.options, options = {};
    if (form.platform === "binary_sensor") { options.inverting = !!o.inverting; if (o.type) options.type = o.type; }
    else if (form.platform === "sensor") { if (o.unit_of_measurement) options.unit_of_measurement = o.unit_of_measurement; }
    else {
      if (form.platform === "light") options.dimmable = !!o.dimmable;
      if (o.on_id) options.on_id = o.on_id;
      if (o.off_id) options.off_id = o.off_id;
    }
    return { platform: form.platform, id, name: form.name, note: form.note, position: form.position, options };
  }

  _previewSoon(delay = 300) {
    clearTimeout(this._previewTimer);
    this._previewTimer = setTimeout(async () => {
      const m = this._modal; if (!m || m.step !== "form") return;
      try {
        const res = await this._ws({ type: "viewmyihc/entity/snippet", entry: this._entryFromForm() });
        const el = this.shadowRoot.querySelector(".preview pre"); if (!el) return;
        el.textContent = res.ok ? res.yaml : Object.entries(res.errors).map(([k, v]) => `# ${k}: ${v}`).join("\n");
      } catch (_e) { /* the preview is optional */ }
    }, delay);
  }

  // The "Create" button: check once more that the entity does not exist yet, then show the entry and where it goes.
  async _createYaml() {
    const m = this._modal; if (!m || m.busy) return;
    m.busy = true; this._renderModal();
    try {
      const res = await this._ws({ type: "viewmyihc/entity/snippet", entry: this._entryFromForm() });
      m.busy = false;
      if (!res.ok) { m.errors = res.errors || {}; this._renderModal(); return; }
      if (res.blocked) { await this._loadExisting(); m.errors = { _: this.t("existsBlocked").replace("{platform}", this.tk("platform", m.form.platform)).replace("{entity}", res.same_platform.map((e) => e.entity_id || e.name).join(", ")) }; this._renderModal(); return; }
      m.result = res; m.step = "result"; m.verify = null;
      this._renderModal();
    } catch (e) { m.busy = false; m.errors = { _: (e && (e.message || e.code)) || String(e) }; this._renderModal(); }
  }

  // After the user pasted the entry: is it in the YAML yet, or already loaded into Home Assistant?
  async _verifyInserted() {
    const m = this._modal; if (!m || !m.result) return;
    m.verify = { busy: true }; this._renderModal();
    try {
      const res = await this._ws({ type: "viewmyihc/entity/snippet", entry: this._entryFromForm() });
      const found = res.ok ? res.same_platform[0] : null;
      m.verify = { busy: false, found };
      if (found) { this._loadExisting(); this._loadEntityRows(); }
    } catch (e) { m.verify = { busy: false, error: (e && (e.message || e.code)) || String(e) }; }
    this._renderModal();
  }

  _placementText(p, platform) {
    const code = (s) => `<code>${esc(s)}</code>`;
    const key = p.key && p.key.file ? this.t("whereKey").replace("{platform}", platform).replace("{kfile}", code(p.key.file)).replace("{kline}", p.key.line) : "";
    switch (p.mode) {
      case "append": return this.t("whereAppend").replace("{file}", code(p.file)).replace("{line}", p.after_line) + key;
      case "add_key": return this.t("whereAddKey").replace("{file}", code(p.file)).replace("{line}", p.after_line).replace("{platform}", platform);
      case "new_file": return this.t("whereNewFile").replace("{dir}", code(p.dir));
      default: return this.t("whereManual").replace("{platform}", platform);
    }
  }

  _renderModal() {
    const host = this.shadowRoot.querySelector(".modal-host");
    const m = this._modal;
    if (!host) return;
    if (!m) { host.innerHTML = ""; return; }
    const d = m.detail;
    const resource = `<div class="resource">
        <ha-icon icon="${iconFor({ category: "resource", kind: m.suggest.kind, tag: d?.tag || "" })}"></ha-icon>
        <div class="rinfo"><div class="rname">${esc(d?.name || "")}</div><div class="rpath">${esc((d?.path || []).slice(0, -1).map((p) => p.name).join(" › "))}</div></div></div>`;
    let inner;
    if (m.step === "result") {
      const r = m.result, v = m.verify;
      let verify = "";
      if (v && v.busy) verify = `<div class="checkstatus wait"><span class="spinner small"></span><div>${esc(this.t("checking"))}</div></div>`;
      else if (v && v.error) verify = `<div class="checkstatus err"><ha-icon icon="mdi:alert-circle-outline"></ha-icon><div>${esc(v.error)}</div></div>`;
      else if (v && v.found) verify = `<div class="checkstatus ok"><ha-icon icon="mdi:check-circle-outline"></ha-icon><div><strong>${esc(v.found.source === "yaml"
        ? this.t("verifyFoundYaml").replace("{file}", v.found.file).replace("{line}", v.found.line)
        : this.t("verifyFoundEntity").replace("{entity}", v.found.entity_id))}</strong></div></div>`;
      else if (v) verify = `<div class="checkstatus wait"><ha-icon icon="mdi:help-circle-outline"></ha-icon><div>${esc(this.t("verifyNone"))}</div></div>`;
      inner = `<div class="dlg-body">
          ${resource}
          <h4 class="tight">${esc(this.t("yourEntry"))}</h4>
          <div class="codebox"><button class="btn small" data-act="copy-yaml">${esc(this.t("copyYaml"))}</button><pre>${esc(r.placement.text)}</pre></div>
          <p class="where">${this._placementText(r.placement, m.form.platform)}</p>
          <ol class="steps"><li>${esc(this.t("step1"))}</li><li>${esc(this.t("step2"))}</li><li>${esc(this.t("stepRestart"))}</li></ol>
          ${verify}
        </div>
        <footer><button class="btn-text" data-act="modal-back">${esc(this.t("back"))}</button>
          <button class="btn-text" data-act="verify-yaml" ${v && v.busy ? "disabled" : ""}>${esc(this.t("verifyBtn"))}</button>
          <button class="btn" data-act="modal-close">${esc(this.t("close"))}</button></footer>`;
    } else {
      const f = m.form;
      const err = (k) => (m.errors[k] ? `<div class="ferr">${esc(m.errors[k])}</div>` : "");
      const taken = this._takenPlatforms(m);
      const platforms = m.suggest.platforms.map((p) => {
        const sel = f.platform === p.platform, isTaken = taken.has(p.platform), ok = p.available && !isTaken;
        return `<label class="ptype ${sel ? "sel" : ""} ${ok ? "" : "off"}" title="${esc(isTaken ? this.t("existsBlocked").replace("{platform}", this.tk("platform", p.platform)).replace("{entity}", this._existingNames(m.id, p.platform)) : p.available ? this.tk("platformHelp", p.platform) : p.reason)}">
          <input type="radio" name="platform" value="${p.platform}" ${sel ? "checked" : ""} ${ok ? "" : "disabled"} />
          ${isTaken ? `<span class="badge taken">${esc(this.t("takenBadge"))}</span>` : ""}
          <ha-icon icon="${PLATFORM_ICON[p.platform]}"></ha-icon><span class="pl">${esc(this.tk("platform", p.platform))}</span>
          ${m.suggest.default_platform === p.platform && !isTaken ? `<span class="badge">${esc(this.t("suggested"))}</span>` : ""}</label>`;
      }).join("");
      const ideas = (m.suggest.name_suggestions || []).filter((n) => n !== f.name)
        .map((n) => `<button type="button" class="idea" data-act="pick-name" data-value="${esc(n)}">${esc(n)}</button>`).join("");
      const o = f.options;
      let opts = "";
      if (f.platform === "binary_sensor") {
        opts = `<label class="switchrow"><input type="checkbox" data-f="options.inverting" ${o.inverting ? "checked" : ""}/><span>${esc(this.t("inverting"))}</span></label>
          <label class="field"><span class="lbl2">${esc(this.t("deviceClass"))}</span><span class="withicon"><ha-icon class="dcicon" icon="${DEVICE_CLASS_ICON[o.type] || NO_CLASS_ICON}"></ha-icon><select data-f="options.type"><option value="">${esc(this.t("noClass"))}</option>
          ${(m.suggest.device_classes || []).map((c) => `<option value="${c}" ${o.type === c ? "selected" : ""}>${c}</option>`).join("")}</select></span>${err("options.type")}</label>`;
      } else if (f.platform === "sensor") {
        opts = `<label class="field"><span class="lbl2">${esc(this.t("unit"))}</span><input data-f="options.unit_of_measurement" list="vmi-units" value="${esc(o.unit_of_measurement || "")}" />
          <datalist id="vmi-units">${["°C", "%", "lx", "W", "kWh", "V", "A", "m³", "ppm"].map((u) => `<option value="${u}">`).join("")}</datalist></label>`;
      } else {
        opts = `${f.platform === "light" ? `<label class="switchrow"><input type="checkbox" data-f="options.dimmable" ${o.dimmable ? "checked" : ""}/><span>${esc(this.t("dimmable"))}</span></label>` : ""}
          <div class="two"><label class="field"><span class="lbl2">${esc(this.t("onId"))}</span><input inputmode="numeric" data-f="options.on_id" value="${esc(o.on_id || "")}" />${err("options.on_id")}</label>
          <label class="field"><span class="lbl2">${esc(this.t("offId"))}</span><input inputmode="numeric" data-f="options.off_id" value="${esc(o.off_id || "")}" />${err("options.off_id")}</label></div>
          <p class="help">${esc(this.t("pulseHelp"))}</p>`;
      }
      inner = `<div class="dlg-body">
          <p class="help lead">${esc(this.t("createYamlLead"))}</p>
          ${resource}
          ${this._existsNotice(m)}
          <label class="field locked"><span class="lbl2">${esc(this.t("idLocked"))}</span>
            <span class="lockedval"><ha-icon icon="mdi:lock-outline"></ha-icon><input value="${m.id}" readonly tabindex="-1" aria-readonly="true" /></span></label>
          <div class="grp"><span class="lbl2">${esc(this.t("entityType"))}</span><div class="ptypes" role="radiogroup">${platforms}</div>${err("platform")}</div>
          <label class="field"><span class="lbl2">${esc(this.t("name"))}</span><input data-f="name" value="${esc(f.name)}" autocomplete="off" />${err("name")}<span class="help">${esc(this.t("nameHelp").replace("{id}", m.id))}</span></label>
          ${ideas ? `<div class="ideas"><span class="dim">${esc(this.t("nameIdeas"))}:</span> ${ideas}</div>` : ""}
          <label class="field"><span class="lbl2">${esc(this.t("note"))}</span><textarea rows="2" data-f="note">${esc(f.note)}</textarea></label>
          <label class="field"><span class="lbl2">${esc(this.t("position"))}</span><input data-f="position" value="${esc(f.position)}" /><span class="help">${esc(this.t("positionHelp"))}</span></label>
          <div class="opts"><span class="lbl2">${esc(this.t("optionsFor").replace("{platform}", this.tk("platform", f.platform)))}</span>${opts}</div>
          ${m.errors._ ? `<div class="ferr box">${esc(m.errors._)}</div>` : ""}
          <details class="preview" open><summary>${esc(this.t("livePreview"))}</summary><pre></pre></details>
        </div>
        <footer><button class="btn-text" data-act="modal-close">${esc(this.t("cancel"))}</button>
          <button class="btn" data-act="make-yaml" ${m.busy || taken.has(f.platform) ? "disabled" : ""}>${esc(m.busy ? this.t("checking") : this.t("makeYaml"))}</button></footer>`;
    }
    host.innerHTML = `<div class="scrim"><div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dlg-title">
        <header><h2 id="dlg-title">${esc(this.t("createEntity"))}</h2><button class="icon-btn" data-act="modal-close" aria-label="${esc(this.t("close"))}"><ha-icon icon="mdi:close"></ha-icon></button></header>
        ${inner}</div></div>`;
    const dlg = host.querySelector(".dialog");
    host.querySelector(".scrim").addEventListener("mousedown", (ev) => { if (ev.target.classList.contains("scrim")) this._closeModal(); });
    dlg.querySelectorAll("[data-f]").forEach((el) => {
      const handler = () => {
        this._modalSet(el.dataset.f, el.type === "checkbox" ? el.checked : el.value);
        if (el.dataset.f === "options.type") dlg.querySelector(".dcicon")?.setAttribute("icon", DEVICE_CLASS_ICON[el.value] || NO_CLASS_ICON);
      };
      el.addEventListener("input", handler); el.addEventListener("change", handler);
    });
    dlg.querySelectorAll('input[name="platform"]').forEach((el) => el.addEventListener("change", () => {
      this._modal.form.platform = el.value; this._renderModal();
    }));
    if (m.step === "form") { setTimeout(() => dlg.querySelector('input[data-f="name"]')?.focus(), 30); this._previewSoon(0); }
  }

  // ------------------------------------------------------------------ events

  _onClick(e) {
    const t = e.target.closest("[data-tab],[data-view],[data-copy],[data-jump],[data-act],[data-entfilter],[data-logview],[data-covfilter],[data-dlsel],[data-repkind],[data-bkkind],.row");
    if (!t) return;
    if (t.dataset.bkkind) { this._bkKind = t.dataset.bkkind; this._loadBackups(); return; }
    if (t.dataset.repkind) { this._rep.kind = t.dataset.repkind; this._loadReport(); return; }
    if (t.dataset.dlsel) { this._select(Number(t.dataset.dlsel)); return; }
    if (t.dataset.logview) { this._logView = t.dataset.logview; this._renderBody(); this._openLog(); return; }
    if (t.dataset.covfilter) { this._covFilter = t.dataset.covfilter; this._renderCoverage(); return; }
    if (t.dataset.entfilter !== undefined) { this._entFilter.platform = t.dataset.entfilter; this._renderBody(); return; }
    if (t.dataset.tab) { this._switchTab(t.dataset.tab); return; }
    if (t.dataset.act && this._onAction(t, e)) return;
    if (t.dataset.view) { this._setView(t.dataset.view); return; }
    if (t.dataset.copy) { e.stopPropagation(); this._copy(t.dataset.copy); return; }
    if (t.dataset.jump) { if (this._tab !== "project") this._switchTab("project"); this._reveal(Number(t.dataset.jump)); return; }
    if (t.dataset.act === "retry") { this._start(); return; }
    if (t.dataset.act === "close") { this._holdEnd(); this._selected = null; this._detail = null; this._renderDetail(); this._renderTree(); this._markDlSelected(); return; }
    if (t.classList.contains("row")) {
      const id = Number(t.dataset.id);
      if (e.target.closest(".chev") && t.dataset.has === "1") this._toggle(id);
      else { this._select(id); if (t.dataset.has === "1") this._toggle(id); }
      if (this._results && !e.target.closest(".chev")) { /* keep results list; detail shows the path */ }
    }
  }

  _onKey(e) {
    if (e.key === "Escape" && this._modal) { this._closeModal(); e.preventDefault(); return; }
    const hold = e.target.closest?.("[data-hold]");
    if (hold) { if ((e.key === " " || e.key === "Enter")) { e.preventDefault(); if (!e.repeat && !hold.disabled) this._holdStart(Number(hold.dataset.hold)); } return; }
    if (e.key === "Enter" && e.target.matches?.("[data-ctl]")) { e.preventDefault(); e.target.parentElement.querySelector('[data-act="ctl-set"]')?.click(); return; }
    const row = e.target.closest?.(".row"); if (!row) return;
    const id = Number(row.dataset.id), has = row.dataset.has === "1";
    const rows = [...this.shadowRoot.querySelectorAll(".row")], i = rows.indexOf(row);
    if (e.key === "ArrowDown") { rows[i + 1]?.focus(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { rows[i - 1]?.focus(); e.preventDefault(); }
    else if (e.key === "ArrowRight" && has && !this._expanded.has(id)) { this._toggle(id); e.preventDefault(); }
    else if (e.key === "ArrowLeft" && has && this._expanded.has(id)) { this._toggle(id); e.preventDefault(); }
    else if (e.key === "Enter" || e.key === " ") { this._select(id); e.preventDefault(); }
  }

  // ------------------------------------------------------------------ styles

  _css() {
    return `
:host { display:block; height:100vh; height:100dvh; overflow:hidden; background:var(--primary-background-color, #fafafa); color:var(--primary-text-color, #212121);
  font-family:var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif); --vmi-radius:var(--ha-card-border-radius, 12px);
  --vmi-border:var(--divider-color, rgba(127,127,127,.25)); --vmi-card:var(--card-background-color, #fff);
  --vmi-sub:var(--secondary-text-color, #727272); --vmi-accent:var(--primary-color, #03a9f4); --vmi-soft:var(--secondary-background-color, #f1f1f1); }
* { box-sizing:border-box; }
.page { display:flex; flex-direction:column; height:100%; }
.bar { display:flex; align-items:center; gap:4px; height:56px; padding:0 8px; background:var(--app-header-background-color, var(--vmi-card));
  color:var(--app-header-text-color, var(--primary-text-color)); border-bottom:1px solid var(--vmi-border); flex:none; }
.bar h1 { font-size:20px; font-weight:400; margin:0 0 0 4px; flex:1; letter-spacing:.2px; }
.controller { background:var(--vmi-soft); color:inherit; border:1px solid var(--vmi-border); border-radius:8px; padding:6px 10px; font:inherit; }
.icon-btn { background:none; border:0; color:inherit; width:40px; height:40px; border-radius:50%; cursor:pointer; display:grid; place-items:center; }
.icon-btn:hover { background:var(--vmi-soft); }
.tabs { display:flex; gap:4px; padding:0 12px; background:var(--vmi-card); border-bottom:1px solid var(--vmi-border); flex:none; }
.tab { background:none; border:0; border-bottom:3px solid transparent; color:var(--vmi-sub); font:inherit; font-weight:500; padding:12px 14px 9px; cursor:pointer; display:flex; gap:8px; align-items:center; }
.tab ha-icon { --mdc-icon-size:20px; }
.tab.active { color:var(--vmi-accent); border-bottom-color:var(--vmi-accent); }
.body { flex:1; min-height:0; overflow:auto; padding:16px; }
.project { display:grid; grid-template-columns:minmax(0,1fr) 400px; gap:16px; height:100%; min-height:0; }
.panel { background:var(--vmi-card); border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); min-height:0; overflow:hidden; display:flex; flex-direction:column; }
.toolbar { display:flex; gap:12px; flex-wrap:wrap; padding:12px; align-items:center; border-bottom:1px solid var(--vmi-border); }
.segmented { display:inline-flex; background:var(--vmi-soft); border-radius:999px; padding:3px; }
.seg { background:none; border:0; font:inherit; font-size:13px; font-weight:500; color:var(--vmi-sub); padding:6px 14px; border-radius:999px; cursor:pointer; }
.seg.active { background:var(--vmi-accent); color:var(--text-primary-color, #fff); }
.search { flex:1; min-width:180px; display:flex; align-items:center; gap:8px; background:var(--vmi-soft); border-radius:999px; padding:0 14px; color:var(--vmi-sub); }
.search input { flex:1; border:0; background:none; outline:0; color:var(--primary-text-color); font:inherit; padding:9px 0; }
.info { display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:8px 16px; font-size:12px; color:var(--vmi-sub); border-bottom:1px solid var(--vmi-border); }
.dot { width:3px; height:3px; border-radius:50%; background:var(--vmi-sub); opacity:.6; }
.tree { overflow:auto; flex:1; padding:6px; }
.row { display:flex; align-items:center; gap:6px; min-height:40px; padding:2px 8px 2px calc(8px + var(--depth,0) * 20px); border-radius:8px; cursor:pointer; outline:0; }
.row:hover { background:var(--vmi-soft); }
.row:focus-visible { box-shadow:inset 0 0 0 2px var(--vmi-accent); }
.row.selected { background:color-mix(in srgb, var(--vmi-accent) 16%, transparent); }
.chev { width:24px; height:24px; flex:none; color:var(--vmi-sub); display:grid; place-items:center; } 
.chev ha-icon, .ico { --mdc-icon-size:20px; }
.ico { color:var(--vmi-sub); flex:none; } .ico.res { color:var(--vmi-accent); }
.cat-group > .name { font-weight:600; } .cat-functionblock > .ico, .cat-product > .ico { color:var(--vmi-accent); }
.name { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:14px; }
.name small { display:block; font-size:11px; color:var(--vmi-sub); overflow:hidden; text-overflow:ellipsis; }
.chip { font:inherit; font-size:11px; border:0; border-radius:999px; padding:3px 9px; background:var(--vmi-soft); color:var(--vmi-sub); display:inline-flex; align-items:center; gap:3px; flex:none; }
.chip ha-icon { --mdc-icon-size:13px; }
.chip.id { font-family:ui-monospace, Menlo, Consolas, monospace; color:var(--primary-text-color); cursor:pointer; }
.chip.id:hover { background:var(--vmi-accent); color:var(--text-primary-color,#fff); }
.val { font-size:12px; font-weight:600; padding:3px 10px; border-radius:999px; flex:none; min-width:0; }
.val:empty { display:none; }
.val.on { background:color-mix(in srgb, var(--success-color, #43a047) 22%, transparent); color:var(--success-color, #2e7d32); }
.val.off { background:var(--vmi-soft); color:var(--vmi-sub); }
.val.num, .val.txt { background:color-mix(in srgb, var(--vmi-accent) 14%, transparent); color:var(--primary-text-color); font-variant-numeric:tabular-nums; }
.val.none { background:none; color:var(--vmi-sub); }
.no-results { text-align:center; color:var(--vmi-sub); padding:32px; }
.detail-panel { overflow:auto; padding:20px; }
.placeholder { display:grid; align-content:start; justify-items:start; gap:10px; color:var(--vmi-sub); padding:4px 2px; line-height:1.5; } .placeholder h3 { margin:0; color:var(--primary-text-color); font-size:16px; font-weight:500; text-transform:none; letter-spacing:0; } .placeholder ol { margin:0; padding-left:20px; font-size:13px; } .placeholder li { margin:4px 0; }
.placeholder ha-icon { --mdc-icon-size:40px; opacity:.5; }
.d-head h2 { margin:6px 0 6px; font-size:20px; font-weight:500; line-height:1.25; }
.d-type { display:inline-flex; align-items:center; gap:6px; font-size:12px; color:var(--vmi-accent); font-weight:600; text-transform:uppercase; letter-spacing:.6px; }
.d-type ha-icon { --mdc-icon-size:18px; }
.d-close { display:none; position:absolute; right:12px; top:10px; }
.crumbs { display:flex; flex-wrap:wrap; align-items:center; font-size:12px; color:var(--vmi-sub); } .crumbs ha-icon { --mdc-icon-size:14px; }
.idbox { margin:16px 0; padding:14px; border-radius:var(--vmi-radius); background:var(--vmi-soft); display:grid; gap:10px; }
.idbox > div { display:flex; align-items:center; gap:10px; }
.lbl { font-size:11px; text-transform:uppercase; letter-spacing:.6px; color:var(--vmi-sub); min-width:78px; }
.bigid { display:inline-flex; align-items:center; gap:10px; font:inherit; font-family:ui-monospace, Menlo, Consolas, monospace; font-size:24px; font-weight:600; color:var(--primary-text-color); background:none; border:0; cursor:pointer; padding:0; }
.bigid ha-icon { --mdc-icon-size:18px; color:var(--vmi-sub); } .bigid:hover ha-icon { color:var(--vmi-accent); }
code { font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px; } code.dim { color:var(--vmi-sub); }
h3 { font-size:12px; text-transform:uppercase; letter-spacing:.7px; color:var(--vmi-sub); margin:20px 0 8px; font-weight:600; }
.note { white-space:pre-wrap; margin:0; font-size:14px; line-height:1.5; }
dl { display:grid; grid-template-columns:auto 1fr; gap:6px 16px; margin:0; font-size:13px; } dt { color:var(--vmi-sub); } dd { margin:0; word-break:break-word; }
ul { list-style:none; margin:0; padding:0; } .enum li { padding:3px 0; font-size:13px; } .enum code { color:var(--vmi-sub); margin-right:6px; }
.link-item { width:100%; display:flex; gap:8px; align-items:center; text-align:left; background:none; border:1px solid var(--vmi-border); color:inherit; font:inherit; font-size:13px; border-radius:10px; padding:8px 10px; margin-bottom:6px; cursor:pointer; }
.link-item.internal { cursor:default; color:var(--vmi-sub); border-style:dashed; } .link-item.internal ha-icon { color:var(--vmi-sub); }
.link-item:not(.internal):hover { border-color:var(--vmi-accent); background:color-mix(in srgb, var(--vmi-accent) 8%, transparent); }
.link-item ha-icon { --mdc-icon-size:18px; color:var(--vmi-accent); flex:none; } .link-item span { flex:1; } .link-item code { color:var(--vmi-sub); }
.state { display:grid; place-items:center; text-align:center; gap:8px; padding:60px 20px; color:var(--vmi-sub); }
.state.card { max-width:520px; margin:40px auto; background:var(--vmi-card); border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); } .state h2 { margin:0; color:var(--primary-text-color); font-weight:500; }
.state ha-icon { --mdc-icon-size:44px; } .state.err ha-icon { color:var(--error-color, #db4437); }
.btn { background:var(--vmi-accent); color:var(--text-primary-color,#fff); border:0; border-radius:999px; padding:8px 20px; font:inherit; font-weight:500; cursor:pointer; margin-top:8px; }
.spinner { width:36px; height:36px; border-radius:50%; border:3px solid var(--vmi-border); border-top-color:var(--vmi-accent); animation:spin 1s linear infinite; } @keyframes spin { to { transform:rotate(360deg);} }
.admin { max-width:1200px; margin:0 auto; } .banner { display:flex; align-items:center; gap:10px; background:color-mix(in srgb, var(--vmi-accent) 12%, transparent); border-radius:var(--vmi-radius); padding:12px 16px; font-size:13px; margin-bottom:16px; }
.cards { columns:3 320px; column-gap:16px; }
.cards > .acard { break-inside:avoid; display:block; width:100%; margin:0 0 16px; }
.card.acard { background:var(--vmi-card); border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); padding:16px 18px; } .acard h3 { margin:0 0 12px; color:var(--primary-text-color); font-size:15px; text-transform:none; letter-spacing:0; }
.kvrow { display:flex; gap:12px; padding:5px 0; border-bottom:1px solid var(--vmi-border); font-size:13px; } .kvrow:last-child { border-bottom:0; }
.kvrow .k { color:var(--vmi-sub); flex:0 0 42%; } .kvrow .v { flex:1; word-break:break-word; } .kvrow.complex { flex-direction:column; gap:4px; }
.item { background:var(--vmi-soft); border-radius:8px; padding:6px 10px; margin:4px 0; } .dim { color:var(--vmi-sub); } .adm-err { color:var(--error-color,#db4437); display:flex; gap:8px; align-items:center; font-size:13px; }
.toast { position:fixed; left:50%; bottom:24px; transform:translate(-50%, 20px); background:var(--primary-text-color); color:var(--vmi-card); padding:10px 18px; border-radius:8px; font-size:13px; opacity:0; pointer-events:none; transition:all .2s; }
.toast.show { opacity:.95; transform:translate(-50%, 0); }

.banner .grow { flex:1; } .banner .fetched { font-size:12px; color:var(--vmi-sub); }

.admin-bar { position:sticky; top:0; z-index:4; display:flex; align-items:center; gap:10px; padding:10px 14px; margin-bottom:12px; border-radius:var(--vmi-radius); font-size:13px; border:1px solid transparent; box-shadow:0 2px 10px rgba(0,0,0,.12); transition:opacity .3s, transform .3s; overflow:hidden; }
.admin-bar.leaving { opacity:0; transform:translateY(-6px); }
.admin-bar .msg { flex:1; line-height:1.35; } .admin-bar ha-icon { --mdc-icon-size:20px; flex:none; }
.admin-bar.info { background:color-mix(in srgb, var(--vmi-accent) 14%, var(--vmi-card)); border-color:color-mix(in srgb, var(--vmi-accent) 40%, transparent); }
.admin-bar.ok { background:color-mix(in srgb, var(--success-color,#43a047) 16%, var(--vmi-card)); border-color:color-mix(in srgb, var(--success-color,#43a047) 45%, transparent); } .admin-bar.ok ha-icon { color:var(--success-color,#2e7d32); }
.admin-bar.warn { background:color-mix(in srgb, #ffb300 20%, var(--vmi-card)); border-color:#ffb300; } .admin-bar.warn ha-icon { color:#e08a00; }
.admin-bar.error { background:color-mix(in srgb, var(--error-color,#db4437) 14%, var(--vmi-card)); border-color:var(--error-color,#db4437); } .admin-bar.error ha-icon { color:var(--error-color,#db4437); }
.admin-bar.spin::after { content:""; position:absolute; left:0; bottom:0; height:3px; width:40%; background:var(--vmi-accent); animation:vmi-slide 1.2s ease-in-out infinite; }
@keyframes vmi-slide { 0% { left:-40%; } 100% { left:100%; } }
.spinner.small { width:16px; height:16px; border-width:2px; flex:none; } .icon-btn.tiny { width:28px; height:28px; } .icon-btn.tiny ha-icon { --mdc-icon-size:16px; }
.kvrow.chg { background:color-mix(in srgb, #ffb300 18%, transparent); border-radius:6px; margin:0 -6px; padding-left:6px; padding-right:6px; }
.star { color:#f5a300; margin-right:4px; font-size:13px; } .chgv { font-weight:600; }
.chip.chg { background:color-mix(in srgb, #ffb300 24%, transparent); color:var(--primary-text-color); margin-left:10px; font-size:11px; text-transform:none; letter-spacing:0; font-weight:600; }
.acard.changed { border-color:#ffb300; box-shadow:0 0 0 1px #ffb300 inset; }
.item.new { border-left:3px solid #ffb300; position:relative; } .newbadge { position:absolute; right:8px; top:6px; margin:0; }
.removed { margin-top:10px; font-size:12px; color:var(--vmi-sub); } .rm { display:inline-block; margin:2px 6px 2px 0; padding:1px 8px; border-radius:999px; background:color-mix(in srgb, var(--error-color,#db4437) 14%, transparent); text-decoration:line-through; color:var(--primary-text-color); }
.skeleton { display:grid; gap:10px; } .sk { display:block; height:14px; border-radius:6px; background:linear-gradient(90deg, var(--vmi-soft) 25%, color-mix(in srgb, var(--vmi-soft) 55%, var(--vmi-card)) 50%, var(--vmi-soft) 75%); background-size:200% 100%; animation:vmi-shimmer 1.4s infinite; } .sk.t { width:45%; height:18px; } .sk.s { width:70%; }
@keyframes vmi-shimmer { 0% { background-position:200% 0; } 100% { background-position:-200% 0; } }
.btn-text.small { padding:4px 10px; font-size:12px; }
@media (prefers-reduced-motion: reduce) { .admin-bar.spin::after, .sk { animation:none; } }

.checkstatus { display:flex; gap:12px; align-items:flex-start; padding:12px 14px; border-radius:var(--vmi-radius); margin:4px 0 12px; font-size:14px; }
.checkstatus ha-icon { --mdc-icon-size:24px; flex:none; } .checkstatus .help { margin:4px 0 0; font-weight:400; }
.checkstatus.ok { background:color-mix(in srgb, var(--success-color,#43a047) 16%, transparent); } .checkstatus.ok ha-icon { color:var(--success-color,#2e7d32); }
.checkstatus.wait { background:color-mix(in srgb, #ffb300 20%, transparent); } .checkstatus.wait ha-icon { color:#e08a00; }
.checkstatus.err { background:color-mix(in srgb, var(--error-color,#db4437) 14%, transparent); } .checkstatus.err ha-icon { color:var(--error-color,#db4437); }
.acard h3 .right { float:right; margin-top:-4px; text-transform:none; letter-spacing:0; }
.prows { display:grid; gap:2px; margin:6px 0 10px; } .prow { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid var(--vmi-border); font-size:13px; } .prow:last-child { border-bottom:0; }
.prow ha-icon { --mdc-icon-size:20px; color:var(--vmi-sub); } .pname { width:110px; font-weight:500; } .ploc { flex:1; text-align:right; color:var(--vmi-sub); font-size:12px; overflow:hidden; text-overflow:ellipsis; }
.chip.err { background:color-mix(in srgb, var(--error-color,#db4437) 18%, transparent); color:var(--error-color,#c62828); }
.probs { margin:8px 0; display:grid; gap:6px; } .prob { display:flex; gap:10px; align-items:flex-start; font-size:13px; line-height:1.4; padding:8px 10px; border-radius:10px; background:var(--vmi-soft); }
.prob ha-icon { --mdc-icon-size:18px; flex:none; margin-top:1px; } .prob.error ha-icon { color:var(--error-color,#db4437); } .prob.warn ha-icon, .prob.todo ha-icon { color:#e08a00; } .prob.info { color:var(--vmi-sub); }
code.loc { background:var(--vmi-card); border-radius:6px; padding:1px 6px; margin-left:4px; font-size:11px; }
.acard h4 { margin:14px 0 2px; font-size:14px; } .help.foot { display:flex; gap:6px; align-items:flex-start; flex-wrap:wrap; } .help.foot ha-icon { --mdc-icon-size:14px; margin-top:2px; } .help.foot details { flex-basis:100%; }

.chip.ha { color:var(--vmi-accent); gap:3px; } .chip.ha ha-icon { --mdc-icon-size:14px; }
.existbox { display:flex; gap:12px; align-items:flex-start; background:color-mix(in srgb, var(--vmi-accent) 12%, transparent); border:1px solid color-mix(in srgb, var(--vmi-accent) 35%, transparent); border-radius:var(--vmi-radius); padding:12px 14px; margin:0 0 12px; font-size:13px; }
.existbox > ha-icon { --mdc-icon-size:24px; color:var(--vmi-accent); flex:none; } .existbox ul { margin:6px 0 0; display:grid; gap:6px; }
.existbox li { display:flex; gap:8px; align-items:center; } .existbox li > ha-icon { --mdc-icon-size:18px; color:var(--vmi-sub); } .existbox .en { flex:1; display:grid; } .existbox small { color:var(--vmi-sub); }
.linkbtn { background:none; border:0; padding:0; font:inherit; font-weight:600; color:var(--vmi-accent); cursor:pointer; text-align:left; } .linkbtn:hover { text-decoration:underline; }
.badge.taken { position:absolute; top:-8px; right:6px; background:var(--vmi-sub); }
.callout.danger { background:color-mix(in srgb, var(--error-color,#db4437) 14%, transparent); } .callout.danger ha-icon { color:var(--error-color,#db4437); }

.toolbar.flat { padding:0; border:0; margin:6px 0 10px; } .elist { display:grid; }
.erow .est { min-width:0; } .chip.est:empty { display:none; } .chip.est.ok { background:color-mix(in srgb, var(--vmi-accent) 14%, transparent); color:var(--primary-text-color); font-weight:600; }
.where { font-size:13px; margin:8px 0 4px; line-height:1.45; } .steps { margin:6px 0 10px; padding-left:20px; font-size:13px; display:grid; gap:4px; } .steps li { list-style:decimal; }
h4.tight { margin:4px 0 0; font-size:14px; } .help.lead { margin:0 0 4px; }
.version-banner { display:flex; gap:12px; align-items:flex-start; margin:12px 16px 0; padding:12px 16px; border-radius:var(--vmi-radius); background:color-mix(in srgb, var(--warning-color,#ff9800) 20%, transparent); border:1px solid var(--warning-color,#ff9800); font-size:13px; flex:none; } .version-banner[hidden] { display:none; } .version-banner ha-icon { --mdc-icon-size:24px; color:var(--warning-color,#e65100); flex:none; } .version-banner p { margin:4px 0 0; line-height:1.4; }
.btn.wide { width:100%; display:flex; justify-content:center; align-items:center; gap:8px; margin:0 0 4px; padding:10px 20px; }
.btn.small { padding:4px 14px; font-size:12px; margin:0; } .btn:disabled { opacity:.5; cursor:default; }
.btn-text { background:none; border:0; color:var(--vmi-accent); font:inherit; font-weight:500; padding:8px 14px; border-radius:999px; cursor:pointer; } .btn-text:hover { background:var(--vmi-soft); }
.row-act { background:none; border:0; color:var(--vmi-accent); width:30px; height:30px; border-radius:50%; cursor:pointer; display:grid; place-items:center; flex:none; opacity:0; } .row:hover .row-act, .row.selected .row-act, .row:focus-within .row-act { opacity:1; } .row-act:hover { background:color-mix(in srgb, var(--vmi-accent) 16%, transparent); } .row-act ha-icon { --mdc-icon-size:20px; } @media (hover:none) { .row-act { opacity:1; } }
.chip.ent { color:var(--vmi-accent); } .chip.ok { background:color-mix(in srgb, var(--success-color,#43a047) 22%, transparent); color:var(--success-color,#2e7d32); }
.chip.wait { background:color-mix(in srgb, var(--warning-color,#ff9800) 22%, transparent); color:var(--warning-color,#e65100); }
.entities { max-width:900px; margin:0 auto; display:grid; gap:16px; }
.erow { display:flex; align-items:center; gap:10px; padding:10px 0; border-bottom:1px solid var(--vmi-border); } .erow:last-child { border-bottom:0; }
.eico { --mdc-icon-size:24px; color:var(--vmi-accent); } .einfo { flex:1; min-width:0; } .ename { font-size:14px; font-weight:500; } .esub { font-size:12px; color:var(--vmi-sub); }
.icon-btn.danger:hover { color:var(--error-color,#db4437); } .empty-note { padding:8px 0; } .help { font-size:12px; color:var(--vmi-sub); margin:4px 0 8px; line-height:1.4; }
.codebox { position:relative; background:var(--vmi-soft); border-radius:10px; padding:12px 14px; margin:8px 0 12px; } .codebox .btn { position:absolute; right:10px; top:10px; }
pre { margin:0; font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px; white-space:pre-wrap; word-break:break-all; } .files { padding:0 0 0 18px; list-style:disc; font-size:12px; } .small { font-size:12px; }
.scrim { position:fixed; inset:0; background:rgba(0,0,0,.5); display:grid; place-items:center; z-index:20; padding:16px; }
.dialog { background:var(--vmi-card); color:var(--primary-text-color); border-radius:28px; width:min(560px, 100%); max-height:92vh; display:flex; flex-direction:column; box-shadow:0 12px 48px rgba(0,0,0,.4); overflow:hidden; }
.dialog header { display:flex; align-items:center; justify-content:space-between; padding:16px 12px 8px 24px; } .dialog h2 { margin:0; font-size:22px; font-weight:400; }
.dlg-body { padding:8px 24px 16px; overflow:auto; display:grid; gap:14px; } .dialog footer { display:flex; justify-content:flex-end; gap:8px; padding:12px 20px 18px; }
.resource { display:flex; gap:12px; align-items:center; background:var(--vmi-soft); border-radius:14px; padding:10px 14px; } .resource ha-icon { color:var(--vmi-accent); --mdc-icon-size:26px; }
.rname { font-weight:500; } .rpath { font-size:12px; color:var(--vmi-sub); }
.field { display:grid; gap:4px; } .lbl2 { font-size:12px; color:var(--vmi-sub); font-weight:500; }
.field input, .field select, .field textarea { font:inherit; color:var(--primary-text-color); background:var(--vmi-soft); border:1px solid transparent; border-bottom:1px solid var(--vmi-sub); border-radius:8px 8px 0 0; padding:10px 12px; outline:0; width:100%; }
.field input:focus, .field select:focus, .field textarea:focus { border-bottom-color:var(--vmi-accent); box-shadow:0 1px 0 var(--vmi-accent); }
.lockedval { display:flex; align-items:center; gap:8px; background:var(--vmi-soft); border-radius:8px; padding:0 12px; opacity:.85; } .lockedval ha-icon { --mdc-icon-size:18px; color:var(--vmi-sub); }
.lockedval input { background:none; border:0; box-shadow:none; font-family:ui-monospace, Menlo, Consolas, monospace; font-size:16px; font-weight:600; padding:10px 0; }
.two { display:grid; grid-template-columns:1fr 1fr; gap:12px; } .grp { display:grid; gap:6px; }
.ptypes { display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; }
.ptype { position:relative; display:grid; justify-items:center; gap:4px; text-align:center; padding:12px 6px; border:1px solid var(--vmi-border); border-radius:14px; cursor:pointer; font-size:13px; }
.ptype input { position:absolute; opacity:0; pointer-events:none; } .ptype ha-icon { --mdc-icon-size:24px; color:var(--vmi-sub); }
.ptype:hover { background:var(--vmi-soft); } .ptype.sel { border-color:var(--vmi-accent); background:color-mix(in srgb, var(--vmi-accent) 12%, transparent); } .ptype.sel ha-icon { color:var(--vmi-accent); }
.ptype.off { opacity:.4; cursor:not-allowed; } .badge { font-size:10px; font-weight:600; color:var(--text-primary-color,#fff); background:var(--vmi-accent); border-radius:999px; padding:1px 8px; }
.ideas { display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12px; margin-top:-6px; } .idea { font:inherit; font-size:12px; background:none; color:var(--primary-text-color); border:1px solid var(--vmi-border); border-radius:999px; padding:3px 10px; cursor:pointer; } .idea:hover { border-color:var(--vmi-accent); }
.switchrow { display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer; } .switchrow input { width:18px; height:18px; accent-color:var(--vmi-accent); } .opts { display:grid; gap:12px; }
.ferr { color:var(--error-color,#db4437); font-size:12px; margin-top:2px; } .ferr.box { background:color-mix(in srgb, var(--error-color,#db4437) 12%, transparent); padding:10px 12px; border-radius:10px; }
.preview summary { cursor:pointer; font-size:13px; color:var(--vmi-sub); } .preview pre { background:var(--vmi-soft); padding:10px 12px; border-radius:10px; margin-top:6px; }
.done { justify-items:start; } .okmark { --mdc-icon-size:48px; color:var(--success-color,#43a047); } h3.plain { text-transform:none; letter-spacing:0; color:var(--primary-text-color); font-size:18px; margin:0; } .done h4 { margin:8px 0 0; font-size:14px; }
.callout { display:flex; gap:12px; background:color-mix(in srgb, var(--warning-color,#ff9800) 16%, transparent); border-radius:14px; padding:12px 14px; font-size:13px; } .callout ha-icon { color:var(--warning-color,#e65100); flex:none; } .callout p { margin:4px 0 0; }
.tabs { overflow-x:auto; scrollbar-width:none; } .tab { white-space:nowrap; flex:none; }
.tools { max-width:1200px; margin:0 auto; display:grid; gap:16px; } .tools .banner { margin-bottom:0; }
.mod-panel { display:flex; flex-direction:column; } .mod-scroll { overflow:auto; flex:1; padding:12px; display:grid; gap:12px; align-content:start; }
.mod-scroll .banner { margin:0; } .mod-scroll .card.acard { border:0; padding:4px 4px 8px; } .mod-scroll .dl-grid { grid-template-columns:repeat(4, minmax(0, 1fr)); }
@media (min-width: 1500px) { .mod-scroll .dl-grid { grid-template-columns:repeat(8, minmax(0, 1fr)); } }
.dl-cell.selected { border-color:var(--vmi-accent); box-shadow:0 0 0 1px var(--vmi-accent) inset; background:color-mix(in srgb, var(--vmi-accent) 14%, var(--vmi-soft)); }
.d-head .btn-text.small { margin:2px 0 0 -10px; }
.dl-block { margin-top:14px; padding:10px 12px 12px; border:1px solid var(--vmi-border); border-radius:12px;
  background:color-mix(in srgb, var(--vmi-soft) 40%, var(--vmi-card)); }
.dl-block .dl-head { margin:0 0 8px; padding-bottom:8px; border-bottom:1px dashed var(--vmi-border); }
.dl-block .dl-cell.free { background:var(--vmi-card); } .dl-bar { display:flex; align-items:center; gap:10px; font-size:12px; color:var(--vmi-sub); min-height:28px; }
.dl-status { display:inline-flex; align-items:center; gap:8px; } .dl-head { font-size:12px; color:var(--vmi-sub); margin-bottom:6px; font-weight:500; }
.dl-grid { display:grid; grid-template-columns:repeat(8, minmax(0, 1fr)); gap:6px; align-items:start; }
@media (max-width: 900px) { .dl-grid { grid-template-columns:repeat(4, minmax(0, 1fr)); } }
.logbody { display:grid; gap:16px; } .btn-text { display:inline-flex; align-items:center; gap:4px; } .btn-text ha-icon { --mdc-icon-size:18px; }
.dl-cell { display:grid; grid-template-columns:auto 1fr; grid-template-areas:"a n" "a p" "v v"; gap:0 8px; align-items:center; text-align:left;
  font:inherit; font-size:13px; color:inherit; background:var(--vmi-soft); border:1px solid transparent; border-radius:10px; padding:6px 8px; cursor:pointer; min-width:0; }
.dl-cell:hover { border-color:var(--vmi-accent); } .dl-cell.free { cursor:default; opacity:.55; background:none; border:1px dashed var(--vmi-border); grid-template-areas:"a n"; }
.dl-cell.unlinked { border:1px dashed #e08a00; } .dl-cell.outside { border:1px solid var(--error-color,#db4437); background:color-mix(in srgb, var(--error-color,#db4437) 10%, transparent); }
.dl-head { display:flex; align-items:center; gap:8px; flex-wrap:wrap; } .dl-head b { color:var(--primary-text-color); } .dl-type { color:var(--primary-text-color); } .dl-head .chip { margin:0; }
.dl-addr { grid-area:a; font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px; color:var(--vmi-sub); align-self:start; padding-top:2px; }
.dl-name { grid-area:n; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.dl-cell small { grid-area:p; font-size:11px; color:var(--vmi-sub); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.dl-cell .val { grid-area:v; justify-self:start; margin-top:4px; }
.loglines { margin:0; padding:0; font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px; max-height:65vh; overflow:auto; }
.loglines li { list-style:none; padding:4px 8px; border-bottom:1px solid var(--vmi-border); white-space:pre-wrap; word-break:break-word; }
.loglines li.warn { background:color-mix(in srgb, #ffb300 16%, transparent); }
.tablewrap { overflow:auto; max-height:65vh; } .tbl { width:100%; border-collapse:collapse; font-size:13px; }
.tbl th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:var(--vmi-sub); font-weight:600; padding:6px 8px; position:sticky; top:0; background:var(--vmi-card); border-bottom:1px solid var(--vmi-border); }
.tbl td { padding:6px 8px; border-bottom:1px solid var(--vmi-border); vertical-align:top; } .tbl td small { display:block; color:var(--vmi-sub); font-size:11px; }
.nowrap { white-space:nowrap; } .jumprow { cursor:pointer; } .jumprow:hover { background:var(--vmi-soft); }
.cmp { display:flex; align-items:flex-end; gap:12px; flex-wrap:wrap; } .cmp .field { flex:1; min-width:220px; } .cmp > ha-icon { margin-bottom:12px; color:var(--vmi-sub); }
.diffcounts { display:flex; gap:8px; flex-wrap:wrap; margin:14px 0 4px; } .diffcounts .chip { font-size:12px; margin:0; }
.link-item span small { display:block; color:var(--vmi-sub); font-size:12px; } .chg-line { font-size:12px; margin-top:3px; }
.plus { color:var(--success-color,#2e7d32); } .minus { color:var(--error-color,#c62828); } .chg-line .minus { text-decoration:line-through; }
.covgroup { border-top:1px solid var(--vmi-border); padding:6px 0; } .covgroup summary { cursor:pointer; font-weight:500; padding:6px 0; }
details.press { margin:8px 0 4px; border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); padding:8px 12px; }
details.press summary { cursor:pointer; display:flex; align-items:center; gap:8px; font-weight:500; font-size:14px; } details.press summary ha-icon { color:var(--vmi-accent); --mdc-icon-size:20px; }
details.press[open] { display:grid; gap:10px; }
.clearbox { display:grid; gap:8px; margin:8px 0 12px; padding:12px 14px; border:1px solid var(--error-color,#db4437); border-radius:var(--vmi-radius);
  background:color-mix(in srgb, var(--error-color,#db4437) 6%, transparent); } .clearbox p { margin:0; font-size:13px; }
.btn-text.danger { color:var(--error-color,#c62828); } .btn.danger { background:var(--error-color,#db4437); }
.settings { max-width:760px; } .settings .acard { display:grid; gap:12px; } .settings .acard h3 { margin-bottom:0; }
.setstatus { display:grid; gap:4px; font-size:13px; } .setstatus > div { display:flex; align-items:center; gap:6px; }
.setstatus ha-icon { --mdc-icon-size:18px; } .setstatus .on ha-icon { color:var(--success-color,#2e7d32); } .setstatus .off ha-icon { color:var(--vmi-sub); }
details.help summary { cursor:pointer; } details.help p { margin:6px 0 0; }
.pw-repeat { display:grid; gap:4px; } .pw-repeat[hidden] { display:none; }
.pw-msg { font-size:12px; min-height:16px; } .pw-msg.ok { color:var(--success-color,#2e7d32); } .pw-msg.bad { color:var(--error-color,#c62828); }
${REPORT_CSS}
.reports { max-width:1200px; } .repkinds { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:10px; margin-bottom:10px; }
.repkind { display:flex; gap:12px; align-items:flex-start; text-align:left; font:inherit; color:inherit; background:none; border:1px solid var(--vmi-border);
  border-radius:12px; padding:12px; cursor:pointer; } .repkind:hover { background:var(--vmi-soft); }
.repkind.sel { border-color:var(--vmi-accent); background:color-mix(in srgb, var(--vmi-accent) 10%, transparent); }
.repkind ha-icon { --mdc-icon-size:28px; color:var(--vmi-accent); flex:none; } .repkind span { display:grid; gap:2px; } .repkind small { color:var(--vmi-sub); font-size:12px; }
.reports .paper { box-shadow:0 1px 6px rgba(0,0,0,.15); overflow-x:auto; }
.reports .formfoot .btn { display:inline-flex; align-items:center; gap:6px; } .reports .formfoot .btn ha-icon { --mdc-icon-size:18px; }
.mapwrap { height:100%; display:flex; flex-direction:column; gap:8px; min-height:420px; }
.maptools { display:flex; align-items:center; gap:6px; flex-wrap:wrap; } .maptools .search { max-width:340px; }
.mapstage { position:relative; flex:1; min-height:0; border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); overflow:hidden;
  background:var(--vmi-card); background-image:radial-gradient(var(--vmi-border) 1px, transparent 1px); background-size:22px 22px; }
.mapsvg { width:100%; height:100%; display:block; touch-action:none; user-select:none; -webkit-user-select:none; cursor:grab; }
.mapsvg:active { cursor:grabbing; }
.mapsvg text { fill:var(--primary-text-color); font-family:inherit; } .mapsvg .t-big { font-size:20px; font-weight:700; fill:#fff; }
.mapsvg .t-sub { font-size:12px; fill:var(--vmi-sub); } .mapsvg .t-sub.on-dark { fill:rgba(255,255,255,.8); }
.mapsvg .t-mod { font-size:15px; font-weight:600; } .mapsvg .t-prod { font-size:14px; font-weight:600; } .mapsvg .t-term { font-size:10px; fill:var(--vmi-sub); }
.mapsvg .t-port { font-size:11px; font-weight:700; fill:var(--vmi-sub); }
.mapsvg .ctrl > rect { fill:var(--vmi-soft); stroke:var(--vmi-accent); stroke-width:2; } .mapsvg .ctrl .ctrl-top { fill:var(--vmi-accent); stroke:none; }
.mapsvg .ctrl, .mapsvg .mod, .mapsvg .prod { cursor:pointer; }
.mapsvg .mod > rect:first-child { fill:var(--vmi-card); stroke:var(--vmi-sub); stroke-width:1.5; } .mapsvg .mod.air > rect:first-child { stroke-dasharray:6 4; }
.mapsvg .mod-band { fill:var(--vmi-soft); }
.mapsvg .term circle { fill:var(--vmi-card); stroke:var(--vmi-sub); stroke-width:1.5; } .mapsvg .term.used circle { stroke:none; }
.mapsvg .term.outside circle { stroke:var(--error-color,#db4437); stroke-width:2.5; }
.mapsvg .prod > rect:first-child { fill:var(--vmi-card); stroke:var(--vmi-border); stroke-width:1.5; } .mapsvg .prod .imgbg { fill:#fff; stroke:var(--vmi-border); }
.mapsvg .cable { fill:none; stroke-width:6; stroke-linecap:round; opacity:.85; } .mapsvg .cable.air { stroke-dasharray:2 10; stroke-width:4; }
.mapsvg .wire { fill:none; stroke-width:2; opacity:.75; } .mapsvg .wire.air { stroke-dasharray:5 6; }
.mapsvg .prod:hover > rect:first-child, .mapsvg .mod:hover > rect:first-child { stroke:var(--vmi-accent); }
.mapsvg.has-sel .wire:not(.hl), .mapsvg.has-sel .cable:not(.hl) { opacity:.12; } .mapsvg.has-sel .prod:not(.hl), .mapsvg.has-sel .mod:not(.hl) { opacity:.35; }
.mapsvg .wire.hl { stroke-width:3.5; opacity:1; } .mapsvg .prod.hl > rect:first-child, .mapsvg .mod.hl > rect:first-child { stroke:var(--vmi-accent); stroke-width:3; }
.mapsvg[data-lod="mid"] .lod1, .mapsvg[data-lod="far"] .lod1, .mapsvg[data-lod="far"] .t-prod, .mapsvg[data-lod="far"] .t-port { display:none; }
.mapcard { position:absolute; left:12px; bottom:12px; width:min(380px, calc(100% - 24px)); max-height:60%; overflow:auto; background:var(--vmi-card);
  border:1px solid var(--vmi-border); border-radius:var(--vmi-radius); box-shadow:0 6px 24px rgba(0,0,0,.25); padding:12px 14px; }
.mapcard header { display:flex; gap:12px; align-items:center; } .mapcard header img { width:52px; height:52px; object-fit:contain; background:#fff; border-radius:6px; }
.mapcard header > ha-icon { --mdc-icon-size:40px; color:var(--vmi-accent); } .mapcard header > div { flex:1; min-width:0; } .mapcard h3 { margin:0; text-transform:none; letter-spacing:0; font-size:15px; color:var(--primary-text-color); }
.maprows { margin:10px 0 0; display:grid; gap:4px; } .maprows li { display:flex; align-items:center; gap:8px; font-size:13px; padding:3px 0; border-bottom:1px solid var(--vmi-border); }
.maprows li:last-child { border-bottom:0; } .maprows code { min-width:58px; color:var(--vmi-sub); } .maprows .grow { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.mapnote { max-width:40%; text-align:right; } @media (max-width: 700px) { .mapnote { display:none; } }
.tbl td small { display:block; color:var(--vmi-sub); font-size:11px; } .tbl .slot { white-space:nowrap; } .acard h4 { display:flex; align-items:center; gap:6px; }
.admin-scene { margin-top:16px; } .admin-scene:empty { display:none; }
.aform { display:grid; gap:10px; } .field.auth { border-top:1px solid var(--vmi-border); padding-top:10px; margin-top:4px; }
.field.auth .lbl2 { display:flex; align-items:center; gap:6px; } .field.auth ha-icon { --mdc-icon-size:16px; color:var(--vmi-accent); } .formfoot { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:4px; }
.acard.editing { border-color:var(--vmi-accent); box-shadow:0 0 0 1px var(--vmi-accent) inset; }
.acard h3 .btn-text.right { float:right; margin-top:-6px; } .switchrow.danger span { color:var(--error-color,#c62828); font-size:13px; }
.tbl.access td:not(:first-child), .tbl.access th:not(:first-child) { text-align:center; width:80px; } .tbl.access input { width:18px; height:18px; accent-color:var(--vmi-accent); }
.ctl { display:grid; gap:10px; margin-bottom:12px; } .ctl-row { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.ctl-row .lbl { min-width:96px; } .ctl-row small { flex-basis:100%; padding-left:106px; margin-top:-6px; }
.ctl .help { margin:-4px 0 4px; } .ctl .seg:disabled { opacity:.5; cursor:default; }
.ctl-edit { display:inline-flex; align-items:center; gap:8px; flex-wrap:wrap; }
.ctl-edit input, .ctl-edit select { font:inherit; color:var(--primary-text-color); background:var(--vmi-soft); border:1px solid var(--vmi-border); border-radius:8px; padding:6px 10px; width:9em; }
.ctl-edit input:focus, .ctl-edit select:focus { outline:2px solid var(--vmi-accent); outline-offset:-1px; }
.holdbtn { display:flex; align-items:center; justify-content:center; gap:10px; width:100%; padding:14px; border-radius:14px; font:inherit; font-weight:600;
  border:2px dashed var(--vmi-accent); background:color-mix(in srgb, var(--vmi-accent) 8%, transparent); color:var(--vmi-accent); cursor:pointer;
  user-select:none; -webkit-user-select:none; touch-action:pan-y; -webkit-touch-callout:none; transition:background .12s, transform .12s; }
.holdbtn:focus-visible { outline:2px solid var(--vmi-accent); outline-offset:2px; }
.holdbtn.holding { border-style:solid; background:var(--vmi-accent); color:var(--text-primary-color,#fff); transform:scale(.98); }
.holdbtn:disabled { opacity:.5; cursor:default; } .holdbtn ha-icon { --mdc-icon-size:22px; }
.withicon { display:flex; align-items:center; gap:10px; } .withicon select { flex:1; } .dcicon { --mdc-icon-size:26px; color:var(--vmi-accent); flex:none; }
@media (max-width: 600px) { .ptypes { grid-template-columns:repeat(2, 1fr); } .two { grid-template-columns:1fr; } .dialog { border-radius:20px; } }
@media (max-width: 900px) {
  .project { grid-template-columns:1fr; }
  .detail-panel { position:fixed; inset:auto 0 0 0; max-height:70vh; border-radius:var(--vmi-radius) var(--vmi-radius) 0 0; box-shadow:0 -8px 30px rgba(0,0,0,.3); transform:translateY(105%); transition:transform .25s; z-index:5; }
  .detail-panel.open { transform:none; } .d-close { display:grid; } .detail-panel .placeholder { display:none; }
  .body { padding:8px; }
}`;
  }
}

customElements.define("viewmyihc-panel", ViewMyIHCPanel);
