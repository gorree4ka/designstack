/**
 * Карта развития: отмечает на карте ступень человека и открывает нужный урок.
 *
 * Сервер рисует карту целиком — все 37 навыков и все написанные уроки. Ответы проверки
 * грейда живут только в браузере (D18), поэтому ступень подставляет скрипт: читает тот же
 * ключ, что и проверка, переводит номер ответа в ступень по `data-grades` и оставляет
 * видимой одну кнопку — на следующую ступень.
 *
 * Без скрипта и без пройденной проверки карта остаётся честной и полной: видно все ступени
 * и какие уроки уже написаны.
 */
( function () {
	'use strict';

	var root = document.querySelector( '[data-map]' );

	if ( ! root ) {
		return;
	}

	var KEY = 'designstack-grade-check';
	var ORDER = [ 'junior', 'middle', 'senior' ];
	var NAMES = { junior: 'Junior', middle: 'Middle', senior: 'Senior' };

	var answers = null;

	try {
		answers = JSON.parse( localStorage.getItem( KEY ) || 'null' );
	} catch ( e ) {
		answers = null;
	}

	if ( ! answers || 'object' !== typeof answers ) {
		return;
	}

	var items = Array.prototype.slice.call( root.querySelectorAll( '[data-map-skill]' ) );
	var known = 0;
	var done = 0;

	items.forEach( function ( item ) {
		var slug = item.getAttribute( 'data-map-skill' );
		var picked = answers[ slug ];

		if ( 'number' !== typeof picked ) {
			return;
		}

		var grades = ( item.getAttribute( 'data-grades' ) || '' ).split( ',' );
		var grade = grades[ picked ] || '';
		var reached = ORDER.indexOf( grade ) + 1; // 0 — ступени нет, 1 — junior, 3 — senior.

		known++;

		var step = item.querySelector( '[data-map-step]' );

		if ( step ) {
			step.hidden = false;
			step.textContent = reached
				? 'Ваша ступень: ' + NAMES[ ORDER[ reached - 1 ] ]
				: 'Ступень пока не взята';
		}

		// Кнопка одна — на следующую ступень. Senior взят: расти внутри карты больше некуда.
		var next = reached < ORDER.length ? ORDER[ reached ] : '';

		if ( ! next ) {
			done++;
			item.classList.add( 'is-done' );
		}

		Array.prototype.forEach.call( item.querySelectorAll( '[data-map-lesson]' ), function ( link ) {
			link.hidden = link.getAttribute( 'data-map-lesson' ) !== next;
		} );

		item.classList.add( 'is-known' );
	} );

	if ( ! known ) {
		return;
	}

	root.classList.add( 'is-personal' );

	var intro = root.querySelector( '[data-map-state]' );

	if ( intro ) {
		intro.textContent = done === known
			? 'Проверка пройдена: по всем отвеченным навыкам взята верхняя ступень карты.'
			: 'Отмечено по вашим ответам: ' + known + ' из ' + items.length +
				'. У каждого навыка открыт вход на следующую ступень.';
	}

	var again = root.querySelector( '[data-map-check]' );

	if ( again ) {
		again.textContent = 'Пройти проверку заново';
		again.className = 'ds-button ds-button--secondary';
	}
}() );
