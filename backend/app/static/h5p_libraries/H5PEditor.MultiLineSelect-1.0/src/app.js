import './listbox.scss';

/**
 * Multi-line select widget
 *
 * @type {MultiLineSelect}
 */
H5PEditor.widgets.multiLineSelect = H5PEditor.MultiLineSelect = (function() {
  /**
   * Multi-line select constructor
   *
   * @param {Object} parent Parent widget
   * @param {Object} field Semantics field
   * @param {Object} params Parameters stored for widget
   * @param {Function} setValue Set new value for widget
   * @constructor
   */
  function MultiLineSelect(parent, field, params, setValue) {
    this.parent = parent;
    this.field = field;
    this.params = params;
    this.setValue = setValue;
    this.value = this.params;
    this.id = H5PEditor.getNextFieldId(this.field);
    this.changes = [];

    /**
     * Append widget to DOM
     *
     * @param {jQuery} $wrapper Element that we will append to
     */
    this.appendTo = $wrapper => {
      const fieldMarkup = H5PEditor.createFieldMarkup(this.field, '', this.id);
      const select = this.createSelect();

      $wrapper[0].innerHTML = fieldMarkup;
      const errors = $wrapper[0].querySelector('.h5p-errors');
      errors.parentNode.insertBefore(select, errors);
      this.select = select;
    };

    /**
     * Toggle list box visibility
     *
     * @param {Boolean} [showBox] Force show/hide the list box
     */
    this.toggleListBox = showBox => {
      const isHidden = this.listBox.classList.contains('hidden');
      showBox = showBox !== undefined ? showBox : isHidden;

      if (!showBox) {
        this.listBox.classList.add('hidden');
        this.selectButton.removeAttribute('aria-expanded');
        return;
      }

      // Show box
      this.listBox.classList.remove('hidden');
      this.selectButton.setAttribute('aria-expanded', 'true');
      this.listBox.focus();
    };

    /**
     * Move vertically between the list box options
     *
     * @param {Boolean} moveUp Move up/down in the list
     */
    this.moveVertically = (moveUp = true) => {
      const selected = this.listBox.querySelector('.focused');

      let next = selected.previousSibling;
      if (moveUp) {
        next = selected.nextSibling;
      }

      // Start/end of list
      if (!next) {
        return;
      }

      // Force show list-box and focus it
      this.toggleListBox(true);
      this.chooseOption(next);
    };

    /**
     * Choose an option from the selector.
     *
     * @param {HTMLElement} [option] Option element
     */
    this.chooseOption = option => {
      const focused = this.listBox.querySelector('.focused');
      if (focused) {
        focused.classList.remove('focused');
        focused.removeAttribute('aria-selected');
      }

      option.classList.add('focused');
      option.setAttribute('aria-selected', 'true');

      // Set new option in the selector
      this.selectButton.innerHTML = option.innerHTML;
      this.listBox.setAttribute('aria-activedescendant', option.id);

      // Update theme
      const buttonId = option.id.split('-');
      this.value = buttonId[buttonId.length - 1];
      this.setValue(this.field, this.value);
      this.triggerListeners(this.value);
    };

    /**
     * Create multi line selector DOM elements
     *
     * @returns {HTMLDivElement} Multi-line select wrapper
     */
    this.createSelect = () => {
      const selectWrapper = document.createElement('div');
      selectWrapper.classList.add('h5p-editor-multi-line-select');

      // Button for opening dropdown
      const select = document.createElement('button');
      select.setAttribute('aria-haspopup', 'listbox');
      select.classList.add('multi-select');
      this.selectButton = select;

      select.addEventListener('click', () => {
        this.toggleListBox();
      });
      select.addEventListener('keydown', e => {
        switch (e.key) {
          case 'Down':
          case 'ArrowDown':
            this.moveVertically();
            e.preventDefault();
            break;
          case 'Up':
          case 'ArrowUp':
            this.moveVertically(false);
            e.preventDefault();
            break;
        }
      });

      // Dropdown
      const listBox = document.createElement('ul');
      listBox.tabIndex = -1;
      listBox.setAttribute('role', 'listbox');
      listBox.classList.add('hidden');
      listBox.classList.add('listbox');

      listBox.addEventListener('keydown', e => {
        switch (e.key) {
          case 'Down':
          case 'ArrowDown':
            this.moveVertically();
            e.preventDefault();
            break;
          case 'Up':
          case 'ArrowUp':
            this.moveVertically(false);
            e.preventDefault();
            break;
          case 'Enter':
          case ' ':
            // Close list-box
            this.selectButton.focus();
            // Prevent click from triggering on select button
            e.preventDefault();
        }
      });

      listBox.addEventListener('blur', e => {
        const ie11Click =
          e.relatedTarget === null &&
          (listBox.contains(document.activeElement) ||
            listBox === document.activeElement);

        const clickedAlternative =
          e.relatedTarget &&
          (listBox.contains(e.relatedTarget) || listBox === e.relatedTarget);

        if (!(clickedAlternative || ie11Click)) {
          this.toggleListBox(false);
        }
      });

      this.listBox = listBox;

      // Generate options for dropdown
      let defaultOption;
      this.field.options.forEach(data => {
        const option = document.createElement('li');
        option.setAttribute('role', 'option');
        option.id = this.id + '-' + data.value;

        const title = document.createElement('div');
        title.classList.add('title');
        title.innerHTML = data.label;

        const description = document.createElement('div');
        description.classList.add('description');
        description.innerHTML = data.description;

        option.appendChild(title);
        option.appendChild(description);

        // Add movement event listeners
        option.addEventListener('keydown', e => {
          switch (e.key) {
            case 'Down':
            case 'ArrowDown':
              this.moveVertically(false);
              e.preventDefault();
              break;
            case 'Up':
            case 'ArrowUp':
              this.moveVertically();
              e.preventDefault();
          }
        });

        option.addEventListener('click', () => {
          this.chooseOption(option);
          this.toggleListBox(false);
        });

        listBox.appendChild(option);

        if (this.params === data.value || !defaultOption) {
          defaultOption = option;
        }
      });

      // Set active option
      this.chooseOption(defaultOption);

      selectWrapper.appendChild(select);
      selectWrapper.appendChild(listBox);

      return selectWrapper;
    };

    /**
     * Trigger an event with new widget value to anyone listening for changes
     *
     * @param {string} value New value of multi-line selector
     */
    this.triggerListeners = value => {
      this.changes.forEach(change => {
        change(value);
      });
    };

    /**
     * Validate this widget. It is always valid.
     *
     * @returns {boolean} Returns validity of widget
     */
    this.validate = () => {
      return true;
    };

    /**
     * Get select wrapper
     *
     * @returns {HTMLDivElement} Multi-line select wrapper
     */
    this.getElement = () => {
      return this.select;
    };
  }

  return MultiLineSelect;
})();
