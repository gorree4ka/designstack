/**
 * Панель полей ресурса: показываем только поля выбранного типа.
 *
 * Тип живёт в таксономии resource_type. В блочном редакторе её рисует
 * собственная панель WordPress, поэтому выбранный тип читаем из хранилища
 * редактора по номерам термов; в классическом редакторе — из радиокнопок
 * метабокса. Без JS видно все группы — это рабочий, хоть и длинный, вариант.
 */
( function () {
	'use strict';

	var GROUPS = [ 'tool', 'learning', 'asset', 'community' ];
	var TYPES = ( window.designstackCoreFields && window.designstackCoreFields.types ) || {};
	var last = null;

	function panel() {
		return document.querySelector( '.ds-core-fields' );
	}

	function apply( type ) {
		var box = panel();

		if ( ! box || type === last ) {
			return;
		}

		last = type;

		GROUPS.forEach( function ( group ) {
			var fieldset = box.querySelector( '[data-group="' + group + '"]' );

			if ( fieldset ) {
				fieldset.hidden = type !== '' && group !== type;
			}
		} );

		box.setAttribute( 'data-current-type', type );
	}

	function fromRadio() {
		var checked = document.querySelector( 'input[name="designstack_core_resource_type"]:checked' );

		return checked ? checked.value : null;
	}

	function fromStore() {
		var editor = window.wp && window.wp.data && window.wp.data.select( 'core/editor' );

		if ( ! editor || ! editor.getEditedPostAttribute ) {
			return null;
		}

		var ids = editor.getEditedPostAttribute( 'resource_type' );

		if ( ! Array.isArray( ids ) ) {
			return null;
		}

		if ( ! ids.length ) {
			return '';
		}

		// Тип ровно один: если куратор выбрал несколько, оставляем последний.
		if ( ids.length > 1 ) {
			window.wp.data.dispatch( 'core/editor' ).editPost( {
				resource_type: [ ids[ ids.length - 1 ] ]
			} );
		}

		return TYPES[ String( ids[ ids.length - 1 ] ) ] || '';
	}

	function sync() {
		var type = fromStore();

		if ( type === null ) {
			type = fromRadio();
		}

		if ( type !== null ) {
			apply( type );
		}
	}

	function today( event ) {
		var button = event.target.closest && event.target.closest( '.ds-core-today' );

		if ( ! button ) {
			return;
		}

		var input = document.getElementById( button.getAttribute( 'data-target' ) );

		if ( input ) {
			var now = new Date();
			var pad = function ( value ) {
				return ( value < 10 ? '0' : '' ) + value;
			};

			input.value = now.getFullYear() + '-' + pad( now.getMonth() + 1 ) + '-' + pad( now.getDate() );
			input.dispatchEvent( new Event( 'change', { bubbles: true } ) );
		}
	}

	function start() {
		document.addEventListener( 'click', today );
		document.addEventListener( 'change', function ( event ) {
			if ( event.target.name === 'designstack_core_resource_type' ) {
				apply( event.target.value );
			}
		} );

		if ( window.wp && window.wp.data && window.wp.data.subscribe ) {
			window.wp.data.subscribe( sync );
		}

		// Метабоксы приезжают позже основной разметки редактора.
		var tries = 0;
		var wait = setInterval( function () {
			tries += 1;
			sync();

			if ( panel() || tries > 60 ) {
				clearInterval( wait );
			}
		}, 250 );
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', start );
	} else {
		start();
	}
} )();
