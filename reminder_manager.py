// ============== Task Reminder =============
async function handleReminderMode() {
  const input = modeTextInput.value.trim();
  if (!input) {
    modeResponse.textContent = '⚠️ Please enter a reminder command.';
    return;
  }

  // --- Teen-friendly command mapping ---
  function mapTeenCommand(cmd) {
    const command = cmd.toLowerCase().trim();
    if (command.startsWith('show')) return 'view';
    if (command.startsWith('due')) return 'check_due';
    if (command.startsWith('add')) return 'add';
    if (command.startsWith('clear')) return 'clear';
    return 'unknown';
  }

  const teenCommand = mapTeenCommand(input);
  if (teenCommand === 'unknown') {
    modeResponse.textContent = '⚠️ Command not recognized. Try "show", "due", "add", or "clear".';
    return;
  }

  try {
    sendBtn.disabled = true;
    modeResponse.textContent = '⏳ Processing your reminder...';

    // Split command + args
    const args = input.split(' ').slice(1).join(' ');
    const payload = {
      userId: currentUserId,
      mode: 'reminder',
      input: teenCommand + (args ? ' ' + args : '')
    };

    const response = await fetch('/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data && data.success) {
      modeResponse.innerHTML = `<strong>📝 Reminder Mode:</strong><br>${data.response.replace(/\n/g, '<br>')}`;

      // --- Render tasks/progress bars ---
      if (data.tasks && data.tasks.length > 0) {
        const container = document.getElementById('reminder-tasks-container');
        container.innerHTML = '';

        data.tasks.forEach(task => {
          const taskDiv = document.createElement('div');
          taskDiv.classList.add('task');

          const label = document.createElement('p');
          label.textContent = task.text;

          const progress = document.createElement('div');
          progress.classList.add('progress-bar');

          const fill = document.createElement('div');
          fill.classList.add('progress-fill');
          const percent = task.percent || 0; 
          fill.style.width = percent + '%';
          fill.textContent = percent + '%';

          progress.appendChild(fill);
          taskDiv.appendChild(label);
          taskDiv.appendChild(progress);
          container.appendChild(taskDiv);
        });
      }

    } else if (data && data.error) {
      modeResponse.textContent = `⚠️ ${data.error}`;
    } else {
      modeResponse.textContent = '⚠️ Unexpected response. Try again!';
    }

  } catch (err) {
    console.error('Reminder mode error:', err);
    modeResponse.textContent = '❌ Failed to process your reminder. Check your network.';
  } finally {
    sendBtn.disabled = false;
  }
}
