/* Browser-only showcase. Curated examples are never represented as live AI results. */
(() => {
  'use strict';
  const data = window.STAGE_CONTENT;
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const state = {lesson: 'u1-l3', phase: 0, revised: false, filter: 'all', tab: 'lesson', persona: 'premise', choice: null};
  const framework = id => data.frameworks.find(f => f.id === id);
  const currentLesson = () => data.lessons.find(l => l.id === state.lesson);
  const storyAnchors = ['story', 'problem', 'process', 'decisions', 'validation'];

  function showTab(name) {
    state.tab = name;
    $$('#experience-tabs [role=tab]').forEach(button => {
      const active = button.dataset.tab === name;
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
      $('#panel-' + button.dataset.tab).hidden = !active;
    });
  }
  function route() {
    const hash = location.hash.slice(1) || 'demo';
    const story = storyAnchors.includes(hash);
    $('#story-page').hidden = !story;
    $('#demo-page').hidden = story;
    $$('[data-page]').forEach(link => {
      if (link.dataset.page === (story ? 'story' : 'demo')) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.title = story ? 'Stage Time — The product story' : 'Stage Time — Speaking practice, thoughtfully built with AI';
    if (['lesson', 'roleplay', 'library'].includes(hash)) {
      showTab(hash);
      $('#experience').scrollIntoView({block:'start'});
    } else if (['demo', 'story'].includes(hash)) window.scrollTo({top:0});
    else if (story) $('#' + hash).scrollIntoView({block:'start'});
  }
  function renderPath() {
    const lesson = currentLesson();
    $('#lesson-path').innerHTML = data.units.map(unit => `<details class="unit" ${unit.n === lesson.unit ? 'open' : ''}><summary><span class="unit-no">${String(unit.n).padStart(2,'0')}</span>${esc(unit.name)}</summary>${data.lessons.filter(l => l.unit === unit.n).map(l => `<button data-lesson="${esc(l.id)}" aria-current="${l.id === state.lesson}">${esc(l.title)}</button>`).join('')}</details>`).join('');
  }
  function lessonExample(lesson) {
    const f = framework(lesson.framework);
    if (f) return {question:f.example_q, answer:f.example_a, label:'Illustrative worked example from the framework library'};
    return {question:lesson.goal, answer:lesson.id === 'u1-l1' ? 'The local app establishes a personal baseline with held notes and a short reading. Later delivery measurements are compared with that baseline. This browser demo does not access your microphone.' : 'In the local app, this lesson moves from the explanation into a recording or practice exercise, followed by feedback. This preview lets you explore the teaching content without recording.', label:'How this lesson works in the local app'};
  }
  function renderLesson() {
    const lesson = currentLesson(), f = framework(lesson.framework);
    const unit = data.units.find(u => u.n === lesson.unit);
    $('#lesson-unit').textContent = `Unit ${lesson.unit} / ${unit.name}`;
    $('#lesson-time').textContent = `${lesson.minutes} min in the local app`;
    $('#lesson-title').textContent = lesson.title;
    $('#lesson-goal').textContent = lesson.goal;
    $$('.steps li').forEach((el,i) => i === state.phase ? el.setAttribute('aria-current','step') : el.removeAttribute('aria-current'));
    $('#lesson-back').hidden = state.phase === 0;
    $('#lesson-next').innerHTML = ['See an example <span aria-hidden="true">→</span>','Explore sample feedback <span aria-hidden="true">→</span>','Try a roleplay <span aria-hidden="true">→</span>'][state.phase];
    if (state.phase === 0) {
      $('#lesson-body').innerHTML = `<p class="teaching">${esc(lesson.teach)}</p>${f ? `<div class="framework-steps">${f.steps.map((step,i) => `<div><b><span class="step-count">${i+1}.</span>${esc(step.label)}</b><p>${esc(step.cue)}</p></div>`).join('')}</div>` : '<div class="coach-note"><b>Small practice, one focus</b>In the local app, this lesson includes a guided exercise. Recording and AI analysis run on your computer.</div>'}`;
    } else if (state.phase === 1) {
      const example = lessonExample(lesson);
      $('#lesson-body').innerHTML = `<div class="prompt"><span class="prompt-label">${f ? 'The question' : 'The exercise'}</span>${esc(example.question)}</div><span class="example-label">${esc(example.label)}</span><p class="sample-answer">${esc(example.answer)}</p>${f ? `<p class="fine-print">Fictional scenario for practice. Any numbers or outcomes in this example are not Stage Time results.<br>Framework attribution: ${esc(f.source)}</p>` : ''}`;
    } else {
      renderFeedback();
    }
  }
  function renderFeedback() {
    const r = state.revised;
    $('#lesson-body').innerHTML = `<div class="example-label">Illustrative feedback card · general delivery example</div><div class="sample-toggle" role="group" aria-label="Compare example attempts"><button data-attempt="first" aria-pressed="${!r}">First attempt</button><button data-attempt="revised" aria-pressed="${r}">Revised attempt</button></div><div class="feedback-heading"><div class="score">${r ? '84' : '68'}<small>sample / 100</small></div><div><h3>${r ? 'A clearer point. Room to breathe.' : 'The idea is there. Give it room.'}</h3><p>${r ? 'A more deliberate pace makes the answer easier to follow.' : 'A direct opening would help the listener find your answer.'}</p></div></div><div class="signal-grid"><div class="signal"><b>Pace</b><strong>${r ? '142' : '178'} <span>wpm</span></strong><span>${r ? 'More deliberate' : 'A touch fast'}</span></div><div class="signal"><b>Filler words</b><strong>${r ? '2' : '7'}</strong><span>${r ? 'Fewer interruptions' : 'Try a pause instead'}</span></div><div class="signal"><b>Answer structure</b><strong>${r ? '4' : '2'} <span>of 4</span></strong><span>Illustrative framework coverage</span></div></div><div class="coach-note"><b>One thing for next time</b>${r ? 'Keep the clear opening. Finish by restating your point in one short sentence, then stop.' : 'Lead with your answer in one sentence. Then give one reason and one concrete example.'}</div><p class="fine-print">These fixed sample values explain the interface; they are not calculated from the previous example, a recording, or your input. They do not demonstrate measured user improvement.</p>`;
  }
  const scenarios = {
    premise: {name:'The challenger', question:'Why should we fund an AI pilot before you have proved it will work?', options:[
      {title:'Reframe the premise',answer:'We are not asking for a full rollout. I would propose a small, time-limited pilot to test whether the idea is useful before we commit more resources.',followup:'What would you measure to decide whether to continue?',note:'You separated a pilot from a rollout. Next, name the success criteria and a clear stopping point.'},
      {title:'Jump straight to the benefits',answer:'AI could save time and help the team work more efficiently. There are a lot of promising possibilities.',followup:'Which possibility would you test first, and how would you know it helped?',note:'The benefits are broad. A bounded use case and a measurable learning goal would make the proposal more concrete.'}
    ]},
    specifics: {name:'The numbers person', question:'Exactly how much time will your proposed workflow save?', options:[
      {title:'Name what is known and unknown',answer:'We do not have that figure yet. I would measure the current task time first, then compare it with a small pilot that includes review time.',followup:'How will you account for the time spent correcting AI output?',note:'You avoided inventing a number and proposed a baseline. Include review and correction effort in the comparison.'},
      {title:'Offer an untested estimate',answer:'I would expect it to save about half the time, based on how quickly AI can produce a first draft.',followup:'Does that estimate include checking the draft and fixing mistakes?',note:'A fast first draft is not the same as a faster completed task. Label assumptions and measure the whole workflow.'}
    ]},
    friendly: {name:'Curious colleague', question:'What is Stage Time, and what did you learn by building it?', options:[
      {title:'Lead with the problem and process',answer:'Stage Time is a speaking-practice prototype. I used BMAD for discovery and brainstorming, Claude to help code it, and personal testing to explore the experience. Next I want to test it with other users.',followup:'What is the first thing you would want to learn from those users?',note:'The answer connects the product, the AI-assisted process, and the next validation step without claiming results you have not measured.'},
      {title:'Start with the feature list',answer:'It has lessons, frameworks, voice analysis, roleplay personas, a question bank, and a local AI model.',followup:'Which user problem brings those features together?',note:'Features become easier to understand when you first explain who they help and what task they support.'}
    ]}
  };
  function renderRoleplay() {
    const s = scenarios[state.persona];
    $('#persona-name').textContent = s.name;
    $('#conversation').innerHTML = `<div class="bubble"><span class="speaker">${esc(s.name)}</span>${esc(s.question)}</div>`;
    if (state.choice === null) {
      $('#roleplay-options').innerHTML = `<p class="small muted" style="margin-top:18px">Choose an example response to see the follow-up.</p><div class="choices">${s.options.map((o,i) => `<button class="choice" data-choice="${i}"><span>${i+1}.</span>${esc(o.title)} <span aria-hidden="true">→</span></button>`).join('')}</div>`;
    } else {
      const o = s.options[state.choice];
      $('#conversation').innerHTML += `<div class="bubble user"><span class="speaker">Example response</span>${esc(o.answer)}</div><div class="bubble"><span class="speaker">${esc(s.name)} · follow-up</span>${esc(o.followup)}</div><div class="coach-note"><b>Illustrative coaching note</b>${esc(o.note)}</div>`;
      $('#roleplay-options').innerHTML = '<button class="text-button" id="roleplay-reset" style="margin-top:20px">← Try the other response</button>';
    }
  }
  function renderLibrary() {
    const query = $('#framework-search').value.trim().toLowerCase();
    const list = data.frameworks.filter(f => (state.filter === 'all' || f.group === state.filter) && `${f.name} ${f.tagline} ${f.best_for.join(' ')} ${f.avoid}`.toLowerCase().includes(query));
    $('#library-count').textContent = `${list.length} ${list.length === 1 ? 'framework' : 'frameworks'}${query ? ' matching your search' : ''}`;
    $('#framework-list').innerHTML = list.length ? list.map(f => `<button class="framework-row" data-framework="${esc(f.id)}"><span class="framework-number">${String(data.frameworks.indexOf(f)+1).padStart(2,'0')}</span><div><span class="framework-name">${esc(f.name)}</span><p>${esc(f.tagline)}</p></div><span class="arrow" aria-hidden="true">↗</span></button>`).join('') : '<p class="empty">No frameworks match. Try a different term or select “All frameworks.”</p>';
  }
  function openFramework(id) {
    const f = framework(id);
    if (!f) return;
    $('#dialog-content').innerHTML = `<span class="eyebrow">From the Stage Time framework library</span><h2 id="dialog-title">${esc(f.name)}</h2><p class="muted small">${esc(f.tagline)}</p><ol class="dialog-steps">${f.steps.map(s => `<li><b>${esc(s.label)}</b><p>${esc(s.cue)}</p></li>`).join('')}</ol><div class="prompt"><span class="prompt-label">Illustrative practice question</span>${esc(f.example_q)}</div><p class="sample-answer">${esc(f.example_a)}</p><p class="fine-print">Fictional worked example. Its figures and outcomes are not claims about Stage Time.</p><p class="dialog-source">Framework attribution: ${esc(f.source)}</p>`;
    $('#framework-dialog').showModal();
  }
  $('#experience-tabs').addEventListener('click', e => {
    const tab = e.target.closest('[data-tab]');
    if (tab) {showTab(tab.dataset.tab); history.replaceState(null,'','#' + tab.dataset.tab);}
  });
  $('#experience-tabs').addEventListener('keydown', e => {
    const tabs = $$('#experience-tabs [role=tab]');
    const current = tabs.indexOf(document.activeElement);
    if (current < 0) return;
    let next;
    if (e.key === 'ArrowRight') next = (current+1)%tabs.length;
    if (e.key === 'ArrowLeft') next = (current-1+tabs.length)%tabs.length;
    if (e.key === 'Home') next = 0;
    if (e.key === 'End') next = tabs.length-1;
    if (next !== undefined) {e.preventDefault();tabs[next].click();tabs[next].focus();}
  });
  $('#lesson-path').addEventListener('click', e => {
    const button = e.target.closest('[data-lesson]');
    if (!button) return;
    state.lesson = button.dataset.lesson; state.phase = 0; state.revised = false;
    renderPath(); renderLesson();
    $('#lesson-title').setAttribute('tabindex','-1'); $('#lesson-title').focus({preventScroll:true});
  });
  $('#lesson-next').addEventListener('click', () => {
    if (state.phase < 2) {state.phase++; renderLesson();}
    else {location.hash = 'roleplay';}
  });
  $('#lesson-back').addEventListener('click', () => {state.phase = Math.max(0,state.phase-1);renderLesson();});
  $('#lesson-body').addEventListener('click', e => {
    const button = e.target.closest('[data-attempt]');
    if (button) {state.revised = button.dataset.attempt === 'revised';renderFeedback();$(`[data-attempt="${state.revised ? 'revised' : 'first'}"]`).focus({preventScroll:true});}
  });
  $('#persona-select').addEventListener('change', e => {state.persona = e.target.value;state.choice = null;renderRoleplay();});
  $('#roleplay-options').addEventListener('click', e => {
    const button = e.target.closest('[data-choice]');
    if (button) {state.choice = Number(button.dataset.choice);renderRoleplay();}
    else if (e.target.closest('#roleplay-reset')) {state.choice = null;renderRoleplay();}
  });
  $('#framework-search').addEventListener('input', renderLibrary);
  $('.library-filters').addEventListener('click', e => {
    const button = e.target.closest('[data-filter]');
    if (!button) return;
    state.filter = button.dataset.filter;
    $$('[data-filter]').forEach(b => b.setAttribute('aria-pressed',String(b === button)));
    renderLibrary();
  });
  $('#framework-list').addEventListener('click', e => {const button = e.target.closest('[data-framework]');if(button) openFramework(button.dataset.framework);});
  $('.dialog-close').addEventListener('click', () => $('#framework-dialog').close());
  $('#framework-dialog').addEventListener('click', e => {if (e.target === $('#framework-dialog')) {const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
  window.addEventListener('hashchange',route);
  renderPath(); renderLesson(); renderRoleplay(); renderLibrary(); route();
})();
