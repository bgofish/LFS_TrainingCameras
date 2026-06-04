<rml>
<head>
</head>
<body data-model="camera_toggle_panel">
<div id="content-wrap"><div id="content">

  <span class="section-label">{{summary}}</span>
  <div class="separator"></div>

  <div class="btn-row">
    <button class="btn" data-event-click="enable_all">Enable all</button>
    <button class="btn" data-event-click="disable_all">Disable all</button>
  </div>
  <div class="separator"></div>

  <span class="section-label">Keep every Nth frame only:</span>
  <div class="setting-row">
    <span class="prop-label">N</span>
    <input type="text" class="number-input" style="width:4em;" data-value="every_n_str" />
    <button class="btn" data-event-click="apply_every_n">Apply</button>
  </div>
  <div class="separator"></div>

  <span class="section-label">Disable frame range (by index):</span>
  <div class="setting-row">
    <span class="prop-label">From</span>
    <input type="text" class="number-input" style="width:4em;" data-value="range_start_str" />
    <span class="prop-label">To</span>
    <input type="text" class="number-input" style="width:4em;" data-value="range_end_str" />
  </div>
  <div class="btn-row">
    <button class="btn" data-event-click="disable_range">Disable range</button>
    <button class="btn" data-event-click="enable_range">Enable range</button>
  </div>
  <div class="separator"></div>

  <div class="btn-row">
    <button class="btn" data-event-click="save_state">Save state</button>
    <button class="btn" data-event-click="load_state">Load &amp; apply</button>
  </div>
  <div class="separator"></div>

  <span class="section-label">Filter:</span>
  <div class="setting-row">
    <input type="text" class="number-input" data-value="filter_str" style="flex:1; min-width:0;" />
  </div>
  <div class="separator"></div>

  <div>{{camera_list}}</div>

</div></div>
</body>
</rml>
