/**
 * Живые куски уроков: чек-лист, секундомер молчания, разметка задания, подбор
 * формата, учебная матрица, разбор заявок, прикидка объёма, конструктор текста
 * и лесенка причин.
 *
 * Общее правило одно и то же во всех: сервер отдаёт страницу, которую можно
 * прочитать целиком, а скрипт превращает её в упражнение. Поэтому содержимое —
 * события сценария, разборы, примеры, тексты исходов — лежит в разметке урока,
 * а здесь только поведение. Ни одной фразы урока в этом файле нет намеренно:
 * иначе содержимое расползлось бы между записью и темой.
 *
 * Кнопки, которые без скрипта были бы мёртвыми, скрипт создаёт сам — в разметке
 * на их месте стоит пустое место (`data-*-actions`).
 */
( function () {
	'use strict';

	/**
	 * Кнопка в стиле сайта. Тексты приходят снаружи, из урока или из вызова.
	 */
	function button( label, kind ) {
		var el = document.createElement( 'button' );

		el.type = 'button';
		el.className = 'ds-button ds-button--sm ds-button--' + ( kind || 'secondary' );
		el.textContent = label;

		return el;
	}

	function pocket( text ) {
		var el = document.createElement( 'span' );

		el.className = 'screen-reader-text';
		el.textContent = ' ' + text;

		return el;
	}

	/* ── чек-лист подготовки ───────────────────────────────────────────────
	   Галочки работают и без скрипта — это обычные checkbox. Скрипт добавляет
	   счётчик: сколько пунктов закрыто и можно ли уже проводить тест. */
	( function () {
		var list = document.querySelector( '[data-checklist]' );

		if ( ! list ) {
			return;
		}

		var boxes = Array.prototype.slice.call( list.querySelectorAll( 'input[type="checkbox"]' ) );
		var fill = document.querySelector( '[data-checklist-fill]' );
		var state = document.querySelector( '[data-checklist-state]' );

		if ( ! boxes.length || ! state ) {
			return;
		}

		function show() {
			var done = boxes.filter( function ( box ) {
				return box.checked;
			} ).length;

			if ( fill ) {
				fill.style.width = Math.round( ( done / boxes.length ) * 100 ) + '%';
			}

			state.textContent = done + ' из ' + boxes.length +
				( done === boxes.length ? ' — можно проводить' : ' — подготовка продолжается' );
		}

		boxes.forEach( function ( box ) {
			box.addEventListener( 'change', show );
		} );

		show();
	}() );

	/* ── секундомер молчания ───────────────────────────────────────────────
	   Без скрипта виден весь учебный сценарий: события с временем и итог
	   «участник нашёл сам». Со скриптом сценарий идёт по секундам, а кнопка
	   подсказки обрывает его и показывает разбор для того момента, когда
	   ведущий не выдержал паузу. */
	( function () {
		var root = document.querySelector( '[data-sim]' );

		if ( ! root ) {
			return;
		}

		var box = root.parentNode;
		var time = root.querySelector( '[data-sim-time]' );
		var log = box.querySelector( '[data-sim-log]' );
		var place = root.querySelector( '[data-sim-controls]' );
		var again = document.querySelector( '[data-sim-actions]' );
		var rows = log ? Array.prototype.slice.call( log.querySelectorAll( '[data-sim-at]' ) ) : [];
		var verdicts = Array.prototype.slice.call( box.querySelectorAll( '[data-sim-verdict]' ) );

		if ( ! time || ! rows.length || ! verdicts.length || ! place ) {
			return;
		}

		var start = button( 'Запустить', 'primary' );
		var help = button( 'Дать подсказку' );
		var reset = button( 'Ещё раз' );
		var from = 0;
		var frame = null;
		var shown = 0;
		var over = false;

		function clock( seconds ) {
			time.innerHTML = seconds.toFixed( 1 ).replace( '.', ',' ) + '<small> с</small>';
		}

		function verdict( key, seconds ) {
			verdicts.forEach( function ( one ) {
				var mine = one.getAttribute( 'data-sim-verdict' ) === key;

				one.hidden = ! mine;

				if ( mine ) {
					var said = one.querySelector( '[data-sim-said]' );

					if ( said ) {
						said.textContent = seconds.toFixed( 1 ).replace( '.', ',' );
					}
				}
			} );
		}

		// Порог разбора — первый из объявленных в уроке, который ещё не прошли.
		function keyFor( seconds ) {
			var key = 'end';

			verdicts.some( function ( one ) {
				var at = parseFloat( one.getAttribute( 'data-sim-verdict' ) );

				if ( at && seconds < at ) {
					key = one.getAttribute( 'data-sim-verdict' );

					return true;
				}

				return false;
			} );

			return key;
		}

		function stop( seconds, won ) {
			over = true;

			if ( frame ) {
				window.cancelAnimationFrame( frame );
			}

			start.disabled = true;
			help.disabled = true;
			reset.hidden = false;
			verdict( won ? 'win' : keyFor( seconds ), seconds );
		}

		function tick() {
			var now = ( window.performance.now() - from ) / 1000;

			clock( now );

			while ( shown < rows.length && now >= parseFloat( rows[ shown ].getAttribute( 'data-sim-at' ) ) ) {
				rows[ shown ].hidden = false;
				shown++;

				if ( shown === rows.length ) {
					stop( now, true );

					return;
				}
			}

			frame = window.requestAnimationFrame( tick );
		}

		function clear() {
			over = false;
			shown = 0;
			rows.forEach( function ( row ) {
				row.hidden = true;
			} );
			verdicts.forEach( function ( one ) {
				one.hidden = true;
			} );
			clock( 0 );
			start.disabled = false;
			help.disabled = true;
			reset.hidden = true;
		}

		start.addEventListener( 'click', function () {
			if ( over ) {
				return;
			}

			from = window.performance.now();
			shown = 0;
			rows.forEach( function ( row ) {
				row.hidden = true;
			} );
			start.disabled = true;
			help.disabled = false;
			frame = window.requestAnimationFrame( tick );
		} );

		help.addEventListener( 'click', function () {
			if ( over ) {
				return;
			}

			stop( ( window.performance.now() - from ) / 1000, false );
		} );

		reset.addEventListener( 'click', clear );

		place.appendChild( start );
		place.appendChild( help );

		if ( again ) {
			again.appendChild( reset );
		}

		// Победный разбор до запуска виден без скрипта; здесь его прячем вместе
		// с лентой — иначе упражнение раскрывает свой же ответ.
		clear();
	}() );

	/* ── разметка задания ──────────────────────────────────────────────────
	   Без скрипта слова-подсказки уже отмечены: страница остаётся объяснением.
	   Со скриптом отметки снимаются, слова становятся кнопками, а разбор
	   открывается только после проверки. */
	( function () {
		var root = document.querySelector( '[data-marks]' );

		if ( ! root ) {
			return;
		}

		var meta = document.querySelector( '[data-marks-meta]' );
		var back = document.querySelector( '[data-marks-back]' );
		var place = document.querySelector( '[data-marks-actions]' );
		var total = parseInt( root.getAttribute( 'data-marks-total' ), 10 ) || 0;

		if ( ! place || ! total ) {
			return;
		}

		var words = [];

		Array.prototype.forEach.call( root.querySelectorAll( '[data-word]' ), function ( span ) {
			var el = document.createElement( 'button' );

			el.type = 'button';
			el.className = 'ds-lesson__word';
			el.textContent = span.textContent;
			el.setAttribute( 'data-word', span.getAttribute( 'data-word' ) );
			el.setAttribute( 'aria-pressed', 'false' );
			span.parentNode.replaceChild( el, span );
			words.push( el );

			el.addEventListener( 'click', function () {
				if ( checked ) {
					return;
				}

				el.classList.toggle( 'is-picked' );
				el.setAttribute( 'aria-pressed', el.classList.contains( 'is-picked' ) ? 'true' : 'false' );
				count();
			} );
		} );

		var check = button( 'Проверить' );
		var checked = false;

		function count() {
			if ( ! meta ) {
				return;
			}

			var picked = words.filter( function ( one ) {
				return one.classList.contains( 'is-picked' );
			} ).length;

			meta.textContent = 'отмечено: ' + picked + ', с подсказкой в этом задании: ' + total;
		}

		check.addEventListener( 'click', function () {
			if ( checked ) {
				checked = false;
				words.forEach( function ( one ) {
					one.className = 'ds-lesson__word';
					one.disabled = false;
					one.setAttribute( 'aria-pressed', 'false' );

					var note = one.querySelector( '.screen-reader-text' );

					if ( note ) {
						one.removeChild( note );
					}
				} );

				if ( back ) {
					back.hidden = true;
				}

				check.textContent = 'Проверить';
				count();

				return;
			}

			checked = true;

			var hit = 0;
			var extra = 0;

			words.forEach( function ( one ) {
				var target = one.getAttribute( 'data-word' ) === '1';
				var picked = one.classList.contains( 'is-picked' );

				one.disabled = true;

				if ( target && picked ) {
					hit++;
					one.appendChild( pocket( '— подсказка, отмечена верно' ) );
				} else if ( target ) {
					one.className = 'ds-lesson__word is-missed';
					one.appendChild( pocket( '— подсказка, пропущена' ) );
				} else if ( picked ) {
					extra++;
					one.className = 'ds-lesson__word is-extra';
					one.appendChild( pocket( '— отмечено лишнее' ) );
				}
			} );

			if ( meta ) {
				meta.textContent = 'Нашли: ' + hit + ' из ' + total +
					( extra ? '. Лишних отмечено: ' + extra : '' );
			}

			if ( back ) {
				back.hidden = false;
			}

			check.textContent = 'Ещё раз';
		} );

		place.appendChild( check );

		if ( back ) {
			back.hidden = true;
		}

		count();
	}() );

	/* ── подбор формата ────────────────────────────────────────────────────
	   Без скрипта видны все четыре вопроса и все исходы: это разбор того, когда
	   какой формат уместен. Со скриптом вопросы идут по одному, а в конце
	   остаётся исход, к которому привели ответы. */
	( function () {
		var root = document.querySelector( '[data-pick]' );

		if ( ! root ) {
			return;
		}

		var steps = Array.prototype.slice.call( root.querySelectorAll( '[data-pick-step]' ) );
		var outs = Array.prototype.slice.call( root.querySelectorAll( '[data-pick-out]' ) );
		var fill = root.querySelector( '[data-pick-fill]' );
		var counter = root.querySelector( '[data-pick-step-of]' );
		var place = root.querySelector( '[data-pick-actions]' );

		if ( steps.length < 2 || outs.length < 2 || ! place ) {
			return;
		}

		var score = {};
		var at = 0;
		var again = button( 'Заново' );

		function show() {
			steps.forEach( function ( step, i ) {
				step.hidden = i !== at;
			} );

			outs.forEach( function ( out ) {
				out.hidden = true;
			} );

			if ( fill ) {
				fill.style.width = Math.round( ( at / steps.length ) * 100 ) + '%';
			}

			if ( counter ) {
				counter.textContent = ( at + 1 ) + ' из ' + steps.length;
			}

			again.hidden = true;
		}

		function finish() {
			var sides = outs.filter( function ( out ) {
				return out.getAttribute( 'data-pick-out' ) !== 'tie';
			} );
			var best = null;
			var tie = false;

			sides.forEach( function ( out ) {
				var key = out.getAttribute( 'data-pick-out' );
				var value = score[ key ] || 0;

				if ( ! best || value > ( score[ best.getAttribute( 'data-pick-out' ) ] || 0 ) ) {
					best = out;
				}
			} );

			tie = sides.every( function ( out ) {
				return ( score[ out.getAttribute( 'data-pick-out' ) ] || 0 ) ===
					( score[ sides[ 0 ].getAttribute( 'data-pick-out' ) ] || 0 );
			} );

			steps.forEach( function ( step ) {
				step.hidden = true;
			} );

			var pick = tie
				? outs.filter( function ( out ) {
					return out.getAttribute( 'data-pick-out' ) === 'tie';
				} )[ 0 ]
				: best;

			outs.forEach( function ( out ) {
				out.hidden = out !== pick;
			} );

			// Счёт по сторонам: названия форматов взяты из разметки урока.
			var table = root.querySelector( '[data-pick-score]' );

			if ( ! table ) {
				table = document.createElement( 'div' );
				table.className = 'ds-lesson__pick-score';
				table.setAttribute( 'data-pick-score', '' );
				place.parentNode.insertBefore( table, place );
			}

			table.innerHTML = '';

			sides.forEach( function ( out ) {
				var key = out.getAttribute( 'data-pick-out' );
				var side = document.createElement( 'div' );

				side.className = 'ds-lesson__pick-side' + ( ! tie && out === best ? ' is-win' : '' );
				side.innerHTML = '<p class="ds-lesson__pick-name">' + ( out.getAttribute( 'data-pick-name' ) || key ) + '</p>' +
					'<span class="ds-lesson__pick-pts">' + ( score[ key ] || 0 ) + '</span> ' +
					'<span class="ds-lesson__pick-lbl">из ' + steps.length + ' ответов</span>';
				table.appendChild( side );
			} );

			if ( fill ) {
				fill.style.width = '100%';
			}

			if ( counter ) {
				counter.textContent = steps.length + ' из ' + steps.length;
			}

			again.hidden = false;
		}

		steps.forEach( function ( step ) {
			Array.prototype.forEach.call( step.querySelectorAll( '[data-pick-side]' ), function ( item ) {
				var el = document.createElement( 'button' );

				el.type = 'button';
				el.className = 'ds-lesson__pick-opt';
				el.innerHTML = item.innerHTML;
				el.setAttribute( 'data-pick-side', item.getAttribute( 'data-pick-side' ) );
				item.parentNode.replaceChild( el, item );

				el.addEventListener( 'click', function () {
					var key = el.getAttribute( 'data-pick-side' );

					score[ key ] = ( score[ key ] || 0 ) + 1;
					at++;

					if ( at < steps.length ) {
						show();

						return;
					}

					finish();
				} );
			} );
		} );

		again.addEventListener( 'click', function () {
			score = {};
			at = 0;

			var table = root.querySelector( '[data-pick-score]' );

			if ( table ) {
				table.parentNode.removeChild( table );
			}

			show();
		} );

		place.appendChild( again );
		show();
	}() );

	/* ── учебная матрица важности ──────────────────────────────────────────
	   Без скрипта это обычная таблица с уровнями, под ней — что каждый уровень
	   значит и пример строки. Со скриптом клетка становится кнопкой и собирает
	   из этих же кусков ответ «строка · сколько из пяти → уровень». */
	( function () {
		var mx = document.querySelector( '[data-mx]' );

		if ( ! mx ) {
			return;
		}

		var out = document.querySelector( '[data-mx-out]' );
		var levels = document.querySelector( '[data-mx-levels]' );
		var examples = document.querySelector( '[data-mx-rows]' );

		if ( ! out || ! levels || ! examples ) {
			return;
		}

		function levelOf( node ) {
			var found = node.className.match( /ds-lesson__sev--([a-z]+)/ );

			return found ? found[ 1 ] : '';
		}

		Array.prototype.forEach.call( mx.querySelectorAll( '[data-mx-row][data-mx-count]' ), function ( cell ) {
			var el = document.createElement( 'button' );

			el.type = 'button';
			el.className = cell.className;
			el.textContent = cell.textContent;
			el.setAttribute( 'data-mx-row', cell.getAttribute( 'data-mx-row' ) );
			el.setAttribute( 'data-mx-count', cell.getAttribute( 'data-mx-count' ) );
			el.setAttribute( 'aria-pressed', 'false' );
			cell.parentNode.replaceChild( el, cell );

			el.addEventListener( 'click', function () {
				Array.prototype.forEach.call( mx.querySelectorAll( '[aria-pressed]' ), function ( other ) {
					other.setAttribute( 'aria-pressed', 'false' );
				} );
				el.setAttribute( 'aria-pressed', 'true' );

				var key = levelOf( el );
				var body = levels.querySelector( '[data-mx-level="' + key + '"]' );
				var title = body && body.previousElementSibling ? body.previousElementSibling.textContent : '';
				var row = examples.querySelector( '[data-mx-row="' + el.getAttribute( 'data-mx-row' ) + '"]' );
				var name = row && row.querySelector( 'b' ) ? row.querySelector( 'b' ).textContent : '';

				out.innerHTML = '';

				var head = document.createElement( 'b' );

				head.textContent = name + ' · ' + el.getAttribute( 'data-mx-count' ) + ' из 5 → ' + title;
				out.appendChild( head );
				out.appendChild( document.createTextNode( body ? body.textContent : '' ) );

				if ( row ) {
					var example = document.createElement( 'span' );

					example.className = 'ds-lesson__dim';
					example.textContent = ' ' + row.textContent.replace( name, '' ).replace( /^\s*—\s*/, 'Пример: ' );
					out.appendChild( example );
				}
			} );
		} );
	}() );

	/* ── разбор заявок на исследование ─────────────────────────────────────
	   Без скрипта у каждой карточки сразу виден ответ — это разбор правил
	   учебной команды. Со скриптом ответ прячется до нажатия, а сверху идёт счёт. */
	( function () {
		var list = document.querySelector( '[data-panel]' );

		if ( ! list ) {
			return;
		}

		var score = document.querySelector( '[data-panel-score]' );
		var items = Array.prototype.slice.call( list.querySelectorAll( '[data-panel-ok]' ) );
		var yes = list.getAttribute( 'data-panel-yes' ) || 'Звать';
		var no = list.getAttribute( 'data-panel-no' ) || 'Не звать';

		if ( ! items.length ) {
			return;
		}

		var right = 0;

		list.classList.add( 'is-live' );

		items.forEach( function ( item ) {
			var place = item.querySelector( '[data-panel-acts]' );

			if ( ! place ) {
				return;
			}

			[ [ '1', yes ], [ '0', no ] ].forEach( function ( pair ) {
				var el = button( pair[ 1 ] );

				el.addEventListener( 'click', function () {
					if ( item.classList.contains( 'is-done' ) ) {
						return;
					}

					var hit = pair[ 0 ] === item.getAttribute( 'data-panel-ok' );

					item.classList.add( 'is-done' );

					Array.prototype.forEach.call( place.children, function ( other ) {
						other.disabled = true;
					} );

					var verdict = item.querySelector( '.ds-lesson__vd' );

					if ( verdict ) {
						verdict.insertBefore( pocket( hit ? 'верно. ' : 'неверно. ' ), verdict.firstChild );
						verdict.insertBefore(
							document.createTextNode( hit ? '✓ ' : '✕ ' ),
							verdict.firstChild
						);
					}

					if ( hit ) {
						right++;
					}

					if ( score ) {
						score.textContent = right + ' из ' + items.length;
					}
				} );

				place.appendChild( el );
			} );
		} );
	}() );

	/* ── прикидка объёма ───────────────────────────────────────────────────
	   Считать без скрипта нечем — это калькулятор. Поэтому все допущения,
	   коэффициенты и тексты лежат в разметке и читаются глазами, даже когда
	   поля не работают. */
	( function () {
		var root = document.querySelector( '[data-calc]' );

		if ( ! root ) {
			return;
		}

		function field( name ) {
			return document.querySelector( '[data-calc-field="' + name + '"]' );
		}

		var users = field( 'users' );
		var share = field( 'share' );
		var unit = field( 'unit' );
		var outcome = field( 'outcome' );
		var shareOut = document.querySelector( '[data-calc-share-out]' );
		var label = document.querySelector( '[data-calc-label]' );
		var out = document.querySelector( '[data-calc-out]' );
		var cap = document.querySelector( '[data-calc-cap]' );
		var say = document.querySelector( '[data-calc-say]' );
		var place = document.querySelector( '[data-calc-actions]' );
		var cases = Array.prototype.slice.call( root.querySelectorAll( '[data-calc-case]' ) );

		if ( ! users || ! share || ! unit || ! outcome || ! out || ! cases.length ) {
			return;
		}

		var first = {
			users: users.value,
			share: share.value,
			unit: unit.value,
			outcome: outcome.value,
		};

		function money( value ) {
			return Math.round( value ).toLocaleString( 'ru-RU' );
		}

		function caseOf() {
			var found = null;

			cases.forEach( function ( one ) {
				if ( one.getAttribute( 'data-calc-case' ) === outcome.value ) {
					found = one;
				}
			} );

			return found || cases[ 0 ];
		}

		function fill( text, affected, low, high ) {
			return text
				.replace( /\{affected\}/g, money( affected ) )
				.replace( /\{lo\}/g, money( low ) )
				.replace( /\{hi\}/g, money( high ) );
		}

		function count() {
			var now = caseOf();
			var people = Math.max( 0, parseFloat( users.value ) || 0 ) * ( parseFloat( share.value ) / 100 );
			var price = Math.max( 0, parseFloat( unit.value ) || 0 );
			var low = people * parseFloat( now.getAttribute( 'data-calc-low' ) ) * price;
			var high = people * parseFloat( now.getAttribute( 'data-calc-high' ) ) * price;
			var capText = now.querySelector( '[data-calc-cap-text]' );
			var sayText = now.querySelector( '[data-calc-say-text]' );

			if ( shareOut ) {
				shareOut.textContent = parseFloat( share.value ) + ' %';
			}

			out.textContent = money( low ) + ' – ' + money( high ) + ' ₽';

			if ( cap && capText ) {
				cap.textContent = capText.textContent;
			}

			if ( say && sayText ) {
				say.innerHTML = fill( sayText.innerHTML, people, low, high );
			}
		}

		outcome.addEventListener( 'change', function () {
			var now = caseOf();

			unit.value = now.getAttribute( 'data-calc-unit' ) || unit.value;

			if ( label ) {
				label.textContent = now.getAttribute( 'data-calc-label' ) || label.textContent;
			}

			count();
		} );

		[ users, share, unit ].forEach( function ( one ) {
			one.addEventListener( 'input', count );
		} );

		if ( place ) {
			var reset = button( 'Сбросить' );

			reset.addEventListener( 'click', function () {
				users.value = first.users;
				share.value = first.share;
				unit.value = first.unit;
				outcome.value = first.outcome;

				var now = caseOf();

				if ( label ) {
					label.textContent = now.getAttribute( 'data-calc-label' ) || label.textContent;
				}

				count();
			} );

			place.appendChild( reset );
		}

		count();
	}() );

	/* ── конструктор текста ────────────────────────────────────────────────
	   Поля слева, готовая формулировка справа. Шаблон и подсказки лежат в разметке
	   урока, здесь только сборка. Синтаксис шаблона тот же, что в конвертере:
	   {поле}, {поле|запасное}, {поле:фильтр}, а кусок {? … ?} выводится, только
	   если все поля внутри него заполнены. Без скрипта в разметке стоит текст,
	   собранный по значениям по умолчанию. */
	( function () {
		var roots = document.querySelectorAll( '[data-build]' );

		if ( ! roots.length ) {
			return;
		}

		function escape( text ) {
			return text.replace( /&/g, '&amp;' ).replace( /</g, '&lt;' ).replace( />/g, '&gt;' );
		}

		var filters = {
			slug: function ( value ) {
				return value.trim().toLowerCase().replace( /\s+/g, '-' ).replace( /[^a-zа-яё0-9-]/gi, '' );
			},
			num: function ( value ) {
				var found = ( value || '' ).match( /(\d+)/ );

				return found ? ( found[ 1 ].length < 2 ? '0' + found[ 1 ] : found[ 1 ] ) : '01';
			},
			ru: function ( value ) {
				var parts = value.split( '-' );

				return 3 === parts.length ? parts.reverse().join( '.' ) : value;
			},
		};

		Array.prototype.forEach.call( roots, function ( root ) {
			var fields = {};
			var outs = Array.prototype.slice.call( root.querySelectorAll( '[data-build-out]' ) );
			var notes = Array.prototype.slice.call( root.querySelectorAll( '[data-build-note]' ) );

			Array.prototype.forEach.call( root.querySelectorAll( '[data-build-field]' ), function ( el ) {
				fields[ el.getAttribute( 'data-build-field' ) ] = el;

				// Дата просмотра — сегодняшняя: это поле человек почти никогда не меняет.
				if ( el.hasAttribute( 'data-build-today' ) && ! el.value ) {
					var now = new Date();

					el.value = now.getFullYear() + '-' + ( '0' + ( now.getMonth() + 1 ) ).slice( -2 ) +
						'-' + ( '0' + now.getDate() ).slice( -2 );
				}
			} );

			if ( ! outs.length ) {
				return;
			}

			function valueOf( name ) {
				return fields[ name ] ? ( fields[ name ].value || '' ).trim() : '';
			}

			function render( template, html ) {
				function field( whole, inner ) {
					var cut = inner.split( '|' );
					var head = cut[ 0 ].split( ':' );
					var value = valueOf( head[ 0 ] );

					if ( 'num' === head[ 1 ] ) {
						return filters.num( value );
					}

					if ( head[ 1 ] && value && filters[ head[ 1 ] ] ) {
						value = filters[ head[ 1 ] ]( value );
					}

					value = value || cut.slice( 1 ).join( '|' );

					return html ? escape( value ) : value;
				}

				var text = template.replace( /\{\?([\s\S]*?)\?\}/g, function ( whole, inner ) {
					var empty = false;

					inner.replace( /\{([^{}?]+)\}/g, function ( match, name ) {
						if ( ! valueOf( name.split( '|' )[ 0 ].split( ':' )[ 0 ] ) ) {
							empty = true;
						}

						return match;
					} );

					return empty ? '' : inner.replace( /\{([^{}?]+)\}/g, field );
				} );

				return text.replace( /\{([^{}?]+)\}/g, field );
			}

			function update() {
				outs.forEach( function ( out ) {
					var html = 'html' === out.getAttribute( 'data-build-mode' );
					var text = render( out.getAttribute( 'data-template' ) || '', html );

					if ( html ) {
						out.innerHTML = text;
					} else {
						out.textContent = text;
					}
				} );

				// Подсказка: первая по порядку, чьё условие выполнено.
				var missing = [];
				var name;

				for ( name in fields ) {
					if ( fields[ name ].hasAttribute( 'data-build-need' ) && ! valueOf( name ) ) {
						missing.push( fields[ name ].getAttribute( 'data-build-need' ) );
					}
				}

				var chosen = null;

				notes.forEach( function ( note ) {
					var when = note.getAttribute( 'data-when' ) || 'ok';
					var holds;

					if ( 'ok' === when ) {
						holds = true;
					} else if ( 'miss' === when ) {
						holds = missing.length > 0;
					} else {
						holds = when.split( /\s+/ ).every( function ( token ) {
							return ! valueOf( token.replace( /^!/, '' ) );
						} );
					}

					if ( holds && ! chosen ) {
						chosen = note;
					}
				} );

				notes.forEach( function ( note ) {
					note.hidden = note !== chosen;

					var list = note.querySelector( '[data-build-miss]' );

					if ( list ) {
						list.textContent = missing.join( ', ' );
					}
				} );
			}

			for ( var key in fields ) {
				fields[ key ].addEventListener( 'input', update );
			}

			update();
		} );
	}() );

	/* ── лесенка причин ────────────────────────────────────────────────────
	   Без скрипта видны все ступени и вывод — это разбор примера. Со скриптом
	   ступени открываются по одной: сначала вопрос «зачем им это», потом ответ. */
	( function () {
		var root = document.querySelector( '[data-dig]' );

		if ( ! root ) {
			return;
		}

		var steps = Array.prototype.slice.call( root.querySelectorAll( '[data-dig-step]' ) );
		var place = document.querySelector( '[data-dig-actions]' );
		var resetPlace = document.querySelector( '[data-dig-reset-place]' );
		var hint = document.querySelector( '[data-dig-hint]' );
		var final = document.querySelector( '[data-dig-final]' );

		if ( steps.length < 2 || ! place ) {
			return;
		}

		var locked = root.getAttribute( 'data-dig-locked' ) || '';
		var next = button( root.getAttribute( 'data-dig-next' ) || 'Дальше', 'primary' );
		var reset = button( root.getAttribute( 'data-dig-reset' ) || 'Сначала' );
		var hintStart = hint ? hint.textContent : '';
		var at = 0;

		// Заглушка у закрытой ступени: текст берётся из урока, место создаёт скрипт.
		steps.forEach( function ( step ) {
			var stub = document.createElement( 'p' );

			stub.setAttribute( 'data-dig-stub', '' );
			stub.textContent = locked;
			stub.hidden = true;

			var body = step.querySelector( '[data-dig-body]' );

			if ( body ) {
				body.parentNode.insertBefore( stub, body.nextSibling );
			}
		} );

		function show() {
			var last = at >= steps.length - 1;

			steps.forEach( function ( step, i ) {
				var body = step.querySelector( '[data-dig-body]' );
				var ask = step.querySelector( '[data-dig-ask]' );
				var stub = step.querySelector( '[data-dig-stub]' );

				step.classList.toggle( 'is-locked', i > at );

				if ( body ) {
					body.hidden = i > at;
				}

				if ( stub ) {
					stub.hidden = i <= at || ! locked;
				}

				if ( ask ) {
					ask.hidden = i !== at;
				}
			} );

			next.hidden = last;
			reset.hidden = ! last;

			if ( final ) {
				final.hidden = ! last;
			}

			if ( hint ) {
				hint.hidden = false;
				hint.textContent = last ? ( hint.getAttribute( 'data-dig-hint-end' ) || hintStart ) : hintStart;
			}
		}

		next.addEventListener( 'click', function () {
			if ( at < steps.length - 1 ) {
				at++;
				show();
			}
		} );

		reset.addEventListener( 'click', function () {
			at = 0;
			show();
		} );

		place.appendChild( next );
		( resetPlace || place ).appendChild( reset );
		show();
	}() );
}() );
