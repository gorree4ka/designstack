/**
 * Фильтры каталога: улучшение, а не условие работы.
 *
 * Без этого файла всё работает: панель раскрывает адрес «#ds-filters», выбор отправляет кнопка
 * «Применить» обычной формой GET. Скрипт добавляет три вещи: удержание фокуса в раскрытой панели
 * и закрытие по Escape (US-18), короткий адрес со значениями через запятую вместо длинного
 * «pricing[]=…», и отправку без кнопки на широком экране.
 */
( function () {
	'use strict';

	var form = document.getElementById( 'ds-filters' );

	if ( ! form ) {
		return;
	}

	var toggle = document.querySelector( '[data-ds-filters-open]' );
	var close = form.querySelector( '[data-ds-filters-close]' );
	var wide = window.matchMedia( '(min-width: 900px)' );
	var timer = null;

	/**
	 * Адрес выдачи по отмеченным значениям: несколько значений одной оси — через запятую.
	 *
	 * @return {string} Адрес.
	 */
	function url() {
		var params = new URLSearchParams();
		var picked = {};

		Array.prototype.forEach.call( form.elements, function ( field ) {
			if ( field.type === 'checkbox' && field.checked ) {
				var key = field.name.replace( /\[\]$/, '' );
				picked[ key ] = picked[ key ] || [];
				picked[ key ].push( field.value );
			}

			if ( field.type === 'hidden' && field.value ) {
				params.set( field.name, field.value );
			}
		} );

		Object.keys( picked ).forEach( function ( key ) {
			params.set( key, picked[ key ].join( ',' ) );
		} );

		// Запятую в адресе оставляем как есть: она законна в строке запроса и читается человеком.
		var query = [];

		params.forEach( function ( value, key ) {
			query.push( encodeURIComponent( key ) + '=' + encodeURIComponent( value ).replace( /%2C/g, ',' ) );
		} );

		return query.length ? form.action + '?' + query.join( '&' ) : form.action;
	}

	form.addEventListener( 'submit', function ( event ) {
		event.preventDefault();
		window.location.assign( url() );
	} );

	// Широкий экран: панель всегда открыта, кнопка не нужна — отправляем после паузы.
	form.addEventListener( 'change', function () {
		if ( ! wide.matches ) {
			return;
		}

		window.clearTimeout( timer );
		timer = window.setTimeout( function () {
			window.location.assign( url() );
		}, 250 );
	} );

	if ( ! toggle ) {
		return;
	}

	/**
	 * Элементы панели, на которые можно встать с клавиатуры.
	 *
	 * @return {Array} Элементы.
	 */
	function stops() {
		return Array.prototype.slice.call(
			form.querySelectorAll( 'a[href], button, input, select, textarea' )
		).filter( function ( node ) {
			return ! node.disabled && node.offsetParent !== null;
		} );
	}

	// Со скриптом панелью управляет атрибут, а не якорь: смена адреса не снимает :target,
	// и после Escape панель осталась бы открытой.
	form.classList.add( 'ds-filters--js' );

	function open() {
		form.setAttribute( 'data-ds-open', 'true' );
		toggle.setAttribute( 'aria-expanded', 'true' );
		var first = stops()[ 0 ];

		if ( first ) {
			first.focus();
		}
	}

	function shut() {
		form.removeAttribute( 'data-ds-open' );
		toggle.setAttribute( 'aria-expanded', 'false' );

		if ( window.location.hash === '#ds-filters' ) {
			history.replaceState( null, '', window.location.pathname + window.location.search );
		}

		toggle.focus();
	}

	toggle.addEventListener( 'click', function ( event ) {
		event.preventDefault();
		open();
	} );

	if ( close ) {
		close.addEventListener( 'click', function ( event ) {
			event.preventDefault();
			shut();
		} );
	}

	document.addEventListener( 'keydown', function ( event ) {
		if ( toggle.getAttribute( 'aria-expanded' ) !== 'true' || wide.matches ) {
			return;
		}

		if ( event.key === 'Escape' ) {
			shut();

			return;
		}

		if ( event.key !== 'Tab' ) {
			return;
		}

		// Пока панель открыта, фокус остаётся внутри неё (US-18).
		var list = stops();

		if ( ! list.length ) {
			return;
		}

		var first = list[ 0 ];
		var last = list[ list.length - 1 ];

		if ( event.shiftKey && document.activeElement === first ) {
			event.preventDefault();
			last.focus();
		} else if ( ! event.shiftKey && document.activeElement === last ) {
			event.preventDefault();
			first.focus();
		}
	} );
}() );
