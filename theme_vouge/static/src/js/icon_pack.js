odoo.define('theme_vouge.icon_pack', function (require) {
'use strict';

	var icofonts = require('wysiwyg.fonts');
	var faIconWidget = require('wysiwyg.widgets.media').IconWidget;
	var core = require('web.core');
	var _t = core._t;
	var InheritUtil = require('web_editor.wysiwyg')
	const OdooEditorLib = require('@web_editor/../lib/odoo-editor/src/OdooEditor');
	const weWidgets = require('wysiwyg.widgets');
	const snippetsEditor = require('web_editor.snippet.editor');
	const Toolbar = require('web_editor.toolbar');
	const getInSelection = OdooEditorLib.getInSelection;
	const preserveCursor = OdooEditorLib.preserveCursor;
	const isBlock = OdooEditorLib.isBlock;
	const OdooEditor = OdooEditorLib.OdooEditor;
	const closestElement = OdooEditorLib.closestElement;

	const wysiwygUtils = require('@theme_vouge/js/utils');
	const faZoomClassRegex = RegExp('fa-[0-9]x');
	const mediaSelector = 'img, .fa, .o_image, .media_iframe_video, .lnr, .icon, .icofont, .lni, .ri, .ti';

	InheritUtil.include({
		start: async function () {
		        const _super = this._super;
		        const self = this;

		        var options = this._editorOptions();
		        this._value = options.value;

		        this.$editable = this.$editable || this.$el;
		        this.$editable.html(this._value);
		        this.$editable.data('wysiwyg', this);
		        this.$editable.data('oe-model', options.recordInfo.res_model);
		        this.$editable.data('oe-id', options.recordInfo.res_id);
		        document.addEventListener('mousedown', this._onDocumentMousedown, true);
		        this.$editable.on('blur', this._onBlur);

		        this.toolbar = new Toolbar(this, this.options.toolbarTemplate);
		        await this.toolbar.appendTo(document.createElement('void'));
		        const commands = this._getCommands();

		        let editorCollaborationOptions;
		        if (options.collaborationChannel) {
		            editorCollaborationOptions = this.setupCollaboration(options.collaborationChannel);
		        }

		        this.odooEditor = new OdooEditor(this.$editable[0], Object.assign({
		            _t: _t,
		            toolbar: this.toolbar.$el[0],
		            document: this.options.document,
		            autohideToolbar: !!this.options.autohideToolbar,
		            isRootEditable: this.options.isRootEditable,
		            placeholder: this.options.placeholder,
		            controlHistoryFromDocument: this.options.controlHistoryFromDocument,
		            getContentEditableAreas: this.options.getContentEditableAreas,
		            defaultLinkAttributes: this.options.userGeneratedContent ? {rel: 'ugc' } : {},
		            getContextFromParentRect: options.getContextFromParentRect,
		            getPowerboxElement: () => {
		                const selection = document.getSelection();
		                if (selection.isCollapsed && selection.rangeCount) {
		                    const node = closestElement(selection.anchorNode, 'P, DIV');
		                    return !(node && node.hasAttribute && node.hasAttribute('data-oe-model')) && node;
		                }
		            },
		            isHintBlacklisted: node => {
		                return node.hasAttribute &&
		                    (node.hasAttribute('data-target') || node.hasAttribute('data-oe-model'));
		            },
		            noScrollSelector: 'body, .note-editable, .o_content, #wrapwrap',
		            commands: commands,
		        }, editorCollaborationOptions));

		        const $wrapwrap = $('#wrapwrap');
		        if ($wrapwrap.length) {
		            $wrapwrap[0].addEventListener('scroll', this.odooEditor.multiselectionRefresh, { passive: true });
		        }

		        if (this._peerToPeerLoading) {
		            this._peerToPeerLoading.then(() => this.ptp.notifyAllClients('ptp_join'));
		        }

		        this._observeOdooFieldChanges();
		        this.$editable.on(
		            'mousedown touchstart',
		            '[data-oe-field]',
		            function () {
		                self.odooEditor.observerUnactive();
		                const $field = $(this);
		                if (($field.data('oe-type') === "datetime" || $field.data('oe-type') === "date")) {
		                    let selector = '[data-oe-id="' + $field.data('oe-id') + '"]';
		                    selector += '[data-oe-field="' + $field.data('oe-field') + '"]';
		                    selector += '[data-oe-model="' + $field.data('oe-model') + '"]';
		                    const $linkedFieldNodes = self.$editable.find(selector).addBack(selector);
		                    $linkedFieldNodes.addClass('o_editable_date_field_linked');
		                    if (!$field.hasClass('o_editable_date_field_format_changed')) {
		                        $linkedFieldNodes.text($field.data('oe-original-with-format'));
		                        $linkedFieldNodes.addClass('o_editable_date_field_format_changed');
		                        $linkedFieldNodes.filter('.oe_hide_on_date_edit').addClass('d-none');
		                        setTimeout(() => {
		                            Wysiwyg.setRange($linkedFieldNodes.filter(':not(.oe_hide_on_date_edit)')[0]);
		                        }, 0);
		                    }
		                }
		                if ($field.data('oe-type') === "monetary") {
		                    $field.attr('contenteditable', false);
		                    $field.find('.oe_currency_value').attr('contenteditable', true);
		                }
		                if ($field.data('oe-type') === "image") {
		                    $field.attr('contenteditable', false);
		                    $field.find('img').attr('contenteditable', true);
		                }
		                if ($field.is('[data-oe-many2one-id]')) {
		                    $field.attr('contenteditable', false);
		                }
		                self.odooEditor.observerActive();
		            }
		        );

		        this.$editable.on('click', '.o_image, .media_iframe_video', e => e.preventDefault());
		        this.showTooltip = true;
		        this.$editable.on('dblclick', mediaSelector, function () {
		            self.showTooltip = false;
		            const $el = $(this);
		            let params = {node: $el};
		            $el.selectElement();
		            if ($el.is('.fa')) {
		                params.htmlClass = [...$el[0].classList].filter((className) => {
		                    return !className.startsWith('fa') || faZoomClassRegex.test(className);
		                }).join(' ');
		            }
		            self.openMediaDialog(params);
		        });
		        this.$editable.on('dblclick', 'a', function (ev) {
		            if (!this.getAttribute('data-oe-model') && self.toolbar.$el.is(':visible')) {
		                self.showTooltip = false;
		                self.toggleLinkTools({
		                    forceOpen: true,
		                    link: this,
		                    noFocusUrl: $(ev.target).data('popover-widget-initialized'),
		                });
		            }
		        });

		        if (options.snippets) {
		            $(this.odooEditor.document.body).addClass('editor_enable');
		            this.snippetsMenu = new snippetsEditor.SnippetsMenu(this, Object.assign({
		                wysiwyg: this,
		                selectorEditableArea: '.o_editable',
		            }, options));
		            await this._insertSnippetMenu();
		        }
		        if (this.options.getContentEditableAreas) {
		            $(this.options.getContentEditableAreas()).find('*').off('mousedown mouseup click');
		        }

		        this._configureToolbar(options);

		        $(this.odooEditor.editable).on('click', this._updateEditorUI.bind(this));
		        $(this.odooEditor.editable).on('keydown', this._updateEditorUI.bind(this));
		        $(this.odooEditor.editable).on('keydown', this._handleShortcuts.bind(this));
		        this._updateEditorUI();
		    },

		openMediaDialog(params = {}) {
			const wysiwygUtils = require('@theme_vouge/js/utils');

			const sel = this.odooEditor.document.getSelection();
	        const fontawesomeIcon = getInSelection(this.odooEditor.document, '.fa');
	        if (fontawesomeIcon && sel.toString().trim() === "") {
	            params.node = $(fontawesomeIcon);
	            params.htmlClass = [...fontawesomeIcon.classList].filter((className) => {
	                return !className.startsWith('fa') || faZoomClassRegex.test(className);
	            }).join(' ');
	        }
	        if (!sel.rangeCount) {
	            return;
	        }
	        const range = sel.getRangeAt(0);
	        const restoreSelection = preserveCursor(this.odooEditor.document);

	        const $node = $(params.node);
	        const $editable = $(OdooEditorLib.closestElement(range.startContainer, '.o_editable'));
	        const model = $editable.data('oe-model');
	        const field = $editable.data('oe-field');
	        const type = $editable.data('oe-type');
	        const mediaParams = Object.assign({
	            res_model: model,
	            res_id: $editable.data('oe-id'),
	            domain: $editable.data('oe-media-domain'),
	            useMediaLibrary: field && (model === 'ir.ui.view' && field === 'arch' || type === 'html'),
	        }, this.options.mediaModalParams, params);
	        const mediaDialog = new weWidgets.MediaDialog(this, mediaParams, $node);
	        mediaDialog.open();

	        mediaDialog.on('save', this, function (element) {
	            if (params.htmlClass) {
	                element.className += " " + params.htmlClass;
	            }
	            restoreSelection();

	            if (wysiwygUtils.isImg($node[0])) {
	                $node.replaceWith(element);
	                this.odooEditor.unbreakableStepUnactive();
	                this.odooEditor.historyStep();
	            } else if (element) {
	                this.odooEditor.execCommand('insertHTML', element.outerHTML);
	            }
	        });
	        mediaDialog.on('closed', this, function () {

	            if (mediaDialog.destroyAction !== 'save') {
	                restoreSelection();
	            }
	        });
		},

	})


	icofonts.fontIcons.push({base: 'lnr', parser: /\.(lnr-(?:\w|-)+)::?before/i});
	icofonts.fontIcons.push({base: 'icon', parser: /\.(icon-(?:\w|-)+)::?before/i});
	icofonts.fontIcons.push({base: 'icofont', parser: /\.(icofont-(?:\w|-)+)::?before/i});
	icofonts.fontIcons.push({base: 'lni', parser: /\.(lni-(?:\w|-)+)::?before/i});
	icofonts.fontIcons.push({base: 'ri', parser: /\.(ri-(?:\w|-)+)::?before/i});
	icofonts.fontIcons.push({base: 'ti', parser: /\.(ti-(?:\w|-)+)::?before/i});

	faIconWidget.include({

		save: function() {
			var lnrf = "{base: 'lnr', font: ''}"
			var iconf = "{base: 'icon', font: ''}"
			var icofontf = "{base: 'icofont', font: ''}"
			var lnif = "{base: 'lni', font: ''}"
			var rif = "{base: 'ri', font: ''}"
			var tif = "{base: 'ti', font: ''}"
			var iconFont = this._getFont(this.selectedIcon) || {base: 'fa', font: ''} || lnrf || iconf || icofontf || lnif || rif || tif;


			if (iconFont.base = "lnr"){
				this.$media.removeClass("icon icofont lni ri ti fa")
			}
			if (iconFont.base = "icon"){
				this.$media.removeClass("lnr icofont lni ri ti fa")
			}
			if (iconFont.base = "icofont"){
				this.$media.removeClass("icon lnr lni ri ti fa")
			}
			if (iconFont.base = "lni"){
				this.$media.removeClass("icon icofont lnr ri ti fa")
			}
			if (iconFont.base = "ri"){
				this.$media.removeClass("icon icofont lni lnr ti fa")
			}
			if (iconFont.base = "ti"){
				this.$media.removeClass("icon icofont lni ri lnr fa")
			}
			if (iconFont.base = "fa"){
				this.$media.removeClass("icon icofont lni ri ti lnr")
			}
			return this._super.apply(this,arguments);
		}
	})

});