/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

// Patch FormController to customize button behavior
patch(FormController.prototype, {
    setup() {
        super.setup();
        this._buttonStates = {
            save: false,
            cancel: false
        };
    },

    /**
     * Override save method to add visual feedback without duplicating text
     */
    async save() {
        const button = document.querySelector('.o_form_button_save');
        if (button && !this._buttonStates.save) {
            // Prevent multiple clicks
            this._buttonStates.save = true;

            // Add loading class
            button.classList.add('o_loading');
            button.disabled = true;
        }

        try {
            const result = await super.save(...arguments);

            // Show success state
            if (button) {
                button.classList.remove('o_loading');
                button.classList.add('o_saved');

                // Show success notification
                this.env.services.notification.add(
                    _t("✅ Başarıyla kaydedildi!"),
                    {
                        type: "success",
                        sticky: false,
                        duration: 3000,
                    }
                );

                // Reset button after animation
                setTimeout(() => {
                    button.classList.remove('o_saved');
                    button.disabled = false;
                    this._buttonStates.save = false;
                }, 1500);
            }

            return result;
        } catch (error) {
            // Reset button on error
            if (button) {
                button.classList.remove('o_loading');
                button.disabled = false;
                this._buttonStates.save = false;
            }

            // Show error notification
            this.env.services.notification.add(
                _t("❌ Kaydetme sırasında hata oluştu!"),
                {
                    type: "danger",
                    sticky: false,
                    duration: 5000,
                }
            );

            throw error;
        }
    },

    /**
     * Override discard method to add confirmation without duplicating text
     */
    async discard() {
        const hasChanges = await this.model.root.isDirty();
        const button = document.querySelector('.o_form_button_cancel');

        if (hasChanges) {
            // Show confirmation dialog
            const confirmed = await this.dialogService.add(ConfirmationDialog, {
                title: _t("⚠️ Değişiklikleri İptal Et"),
                body: _t("Kaydedilmemiş değişiklikler var. İptal etmek istediğinizden emin misiniz?"),
                confirmLabel: _t("Evet, İptal Et"),
                cancelLabel: _t("Hayır, Devam Et"),
                confirmClass: "btn-danger",
            });

            if (!confirmed) {
                return;
            }
        }

        // Add loading state
        if (button && !this._buttonStates.cancel) {
            this._buttonStates.cancel = true;
            button.classList.add('o_loading');
            button.disabled = true;
        }

        try {
            const result = await super.discard(...arguments);

            // Reset button state
            if (button) {
                setTimeout(() => {
                    button.classList.remove('o_loading');
                    button.disabled = false;
                    this._buttonStates.cancel = false;
                }, 500);
            }

            // Show notification
            if (hasChanges) {
                this.env.services.notification.add(
                    _t("↩️ Değişiklikler iptal edildi"),
                    {
                        type: "info",
                        sticky: false,
                        duration: 2000,
                    }
                );
            }

            return result;
        } catch (error) {
            // Reset button on error
            if (button) {
                button.classList.remove('o_loading');
                button.disabled = false;
                this._buttonStates.cancel = false;
            }
            throw error;
        }
    },

    /**
     * Clean up button classes when component is mounted
     */
    onMounted() {
        super.onMounted?.();

        // Remove any Odoo native tooltips
        const buttons = document.querySelectorAll('.o_form_button_save, .o_form_button_cancel');
        buttons.forEach(button => {
            // Remove title and data-tooltip attributes
            button.removeAttribute('title');
            button.removeAttribute('data-tooltip');
            button.removeAttribute('data-bs-toggle');
            button.removeAttribute('data-bs-placement');
            button.removeAttribute('data-bs-original-title');

            // Remove any Bootstrap tooltip instances
            if (button._tooltip) {
                button._tooltip.dispose();
                delete button._tooltip;
            }
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+S or Cmd+S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('.o_form_button_save');
            if (saveButton && !saveButton.disabled && !saveButton.classList.contains('o_loading')) {
                saveButton.click();
            }
        }

        // Escape for cancel (only if not in input field)
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            const isInputField = ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeElement.tagName);

            if (!isInputField) {
                const cancelButton = document.querySelector('.o_form_button_cancel');
                if (cancelButton && !cancelButton.disabled && !cancelButton.classList.contains('o_loading')) {
                    cancelButton.click();
                }
            }
        }
    });
});

// Import ConfirmationDialog
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";