/**
 * Форма «Предложить ресурс»: улучшение, а не условие работы.
 *
 * Без этого файла форма отправляется и проверяется на сервере, ошибки приходят сводкой над формой.
 * Скрипт добавляет две вещи: фокус переходит на сводку ошибок сразу после возврата (US-42),
 * и на время отправки кнопка сообщает о работе, а второй клик не отправляет форму второй раз.
 */
( function () {
	'use strict';

	var form = document.getElementById( 'ds-suggest-form' );

	if ( ! form ) {
		return;
	}

	// Возврат с ошибками: читающий с клавиатуры и экранный чтец попадают сразу на список ошибок.
	// Ставим фокус после загрузки: до неё браузер сам прыгает по якорю адреса и сбрасывает его.
	var summary = form.parentNode.querySelector( '.ds-error-summary' );

	if ( summary ) {
		window.addEventListener( 'load', function () {
			window.setTimeout( function () {
				summary.focus();
			}, 0 );
		} );
	}

	var submit = form.querySelector( '.ds-suggest-form__submit' );

	if ( ! submit ) {
		return;
	}

	var sending = submit.getAttribute( 'data-ds-sending' ) || 'Отправляем…';

	form.addEventListener( 'submit', function ( event ) {
		if ( submit.getAttribute( 'aria-busy' ) === 'true' ) {
			event.preventDefault();

			return;
		}

		// Фон кнопки не бледнеет: она остаётся видимой и озвучивается чтецом (каталог паттернов, правило 7).
		submit.setAttribute( 'aria-busy', 'true' );
		submit.setAttribute( 'aria-disabled', 'true' );
		submit.textContent = sending;
	} );
}() );
