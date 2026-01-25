import { Directive, ElementRef, HostListener } from '@angular/core';

@Directive({
    selector: '[appStrictDateInput]',
    standalone: true
})
export class StrictDateInputDirective {
    private lastValue = '';

    constructor(private el: ElementRef) { }

    @HostListener('input', ['$event'])
    onInput(event: InputEvent) {
        const input = this.el.nativeElement as HTMLInputElement;
        let value = input.value.replace(/\D/g, ''); // Strip non-digits

        // Prevent deletion of slashes by user backspace if they try to delete just a slash
        // But 'mm/dd/yyyy' logic: auto-insert slashes

        if (value.length > 8) {
            value = value.substring(0, 8);
        }

        // Format mm/dd/yyyy
        let formattedDate = '';
        if (value.length > 0) {
            formattedDate = value.substring(0, 2);
            if (value.length >= 2) {
                formattedDate += '/';
                formattedDate += value.substring(2, 4);
            }
            if (value.length >= 4) {
                formattedDate += '/';
                formattedDate += value.substring(4, 8);
            }
        }

        // Update input value only if changed
        if (input.value !== formattedDate) {
            input.value = formattedDate;
            // Trigger input event for Angular forms to pick up change if needed, 
            // but matDatepicker handles its own parsing. 
            // We might need to manually set control value if using reactive forms directly on same input.
        }
    }

    @HostListener('keydown', ['$event'])
    onKeyDown(event: KeyboardEvent) {
        // Allow navigation keys
        if (['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
            return;
        }

        // Allow Copy/Paste
        if ((event.ctrlKey || event.metaKey) && ['a', 'c', 'v', 'x'].includes(event.key.toLowerCase())) {
            return;
        }

        // Block non-numeric keys
        if (!/^\d$/.test(event.key)) {
            event.preventDefault();
        }
    }
}
