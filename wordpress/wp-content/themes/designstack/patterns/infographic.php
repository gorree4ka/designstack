<?php
/**
 * Title: Инфографика выпуска
 * Slug: designstack/infographic
 * Categories: designstack
 * Inserter: no
 *
 * Шесть видов инфографики дайджеста (D190): столбцы, крупные цифры, доля, два списка, схема и механика,
 * плюс «Коротко» и строка «источник · дата». Вёрстка, а не картинка: числа идут текстом и лежат в разметке
 * пользовательскими свойствами (--v, --max, --m, --p, --pmax), столбец и доля — от нуля одной шкалой.
 * На витрине — данные выпуска 30.09.2026. Проверка — scripts/check_infographics.py.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<section class="ds-brief" aria-label="Коротко, образец">
		<p class="ds-brief__title">Коротко</p>
		<ul class="ds-brief__list">
			<li class="ds-brief__item"><a href="#sg-data">В&nbsp;автолейауте Figma появился перенос по&nbsp;вертикали</a></li>
			<li class="ds-brief__item"><a href="#sg-data">Медианная зарплата UX/UI-дизайнера&nbsp;— 120&nbsp;тысяч рублей в&nbsp;месяц</a></li>
		</ul>
	</section>

	<p class="ds-kicker">habr.com · 28&nbsp;сентября</p>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Медианная зарплата UX/UI-дизайнера <span class="ds-infographic__unit">· тыс. ₽ в&nbsp;месяц</span></figcaption>
		<div class="ds-infographic__bars" style="--max: 258; --m: 120">
			<div class="ds-infographic__bar" style="--v: 73"><span>Junior</span><span class="ds-infographic__bar-track" aria-hidden="true"><span class="ds-infographic__bar-fill"></span><span class="ds-infographic__bar-mark"></span></span><span class="ds-infographic__bar-value">около 73</span></div>
			<div class="ds-infographic__bar" style="--v: 127"><span>Middle</span><span class="ds-infographic__bar-track" aria-hidden="true"><span class="ds-infographic__bar-fill"></span><span class="ds-infographic__bar-mark"></span></span><span class="ds-infographic__bar-value">127</span></div>
			<div class="ds-infographic__bar" style="--v: 217"><span>Senior</span><span class="ds-infographic__bar-track" aria-hidden="true"><span class="ds-infographic__bar-fill"></span><span class="ds-infographic__bar-mark"></span></span><span class="ds-infographic__bar-value">217</span></div>
		</div>
		<p class="ds-infographic__legend"><span class="ds-infographic__legend-mark" aria-hidden="true"></span>Пунктир&nbsp;— медиана в&nbsp;целом, 120</p>
		<p class="ds-infographic__source">Хабр Карьера, первое полугодие 2026</p>
	</figure>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Крупные цифры</figcaption>
		<div class="ds-infographic__stats">
			<div class="ds-infographic__stat"><span class="ds-infographic__stat-value">463</span><span class="ds-infographic__stat-label">тестовые сессии</span></div>
			<div class="ds-infographic__stat"><span class="ds-infographic__stat-value">2&nbsp;800+</span><span class="ds-infographic__stat-label">проблем средней и&nbsp;высокой серьёзности</span></div>
			<div class="ds-infographic__stat"><span class="ds-infographic__stat-value">370+</span><span class="ds-infographic__stat-label">рекомендаций</span></div>
		</div>
		<p class="ds-infographic__source">Baymard Institute, 24.09.2026</p>
	</figure>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Доля и шкала <span class="ds-infographic__unit">· 663&nbsp;вопроса</span></figcaption>
		<div class="ds-infographic__share" aria-hidden="true"><span class="ds-infographic__share-part ds-infographic__share-part--1" style="--v: 410"></span><span class="ds-infographic__share-part ds-infographic__share-part--2" style="--v: 160"></span><span class="ds-infographic__share-part ds-infographic__share-part--3" style="--v: 93"></span></div>
		<ul class="ds-infographic__keys">
			<li class="ds-infographic__key"><span class="ds-infographic__swatch ds-infographic__swatch--1" aria-hidden="true"></span><span><b>410</b> по&nbsp;разработке</span></li>
			<li class="ds-infographic__key"><span class="ds-infographic__swatch ds-infographic__swatch--2" aria-hidden="true"></span><span><b>160</b> по&nbsp;редполитике</span></li>
			<li class="ds-infographic__key"><span class="ds-infographic__swatch ds-infographic__swatch--3" aria-hidden="true"></span><span><b>93</b> по&nbsp;дизайну</span></li>
		</ul>
		<div class="ds-infographic__meter"><span>Конкретный ответ</span><b>почти 60&nbsp;%</b><span class="ds-infographic__meter-track" aria-hidden="true"><span class="ds-infographic__meter-fill" style="--v: 60"></span></span></div>
		<p class="ds-infographic__source">Сбер, блог на&nbsp;Хабре, 30.09.2026</p>
	</figure>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Два списка <span class="ds-infographic__unit">· место и&nbsp;баллы</span></figcaption>
		<div class="ds-infographic__lists" style="--pmax: 20">
			<div class="ds-infographic__list">
				<p class="ds-infographic__list-title">Первая десятка</p>
				<ol class="ds-infographic__rank">
					<li class="ds-infographic__rank-item"><span class="ds-infographic__place">1</span><span>Прототипирование с&nbsp;ИИ</span><span class="ds-infographic__pts" style="--p: 20"><span class="ds-infographic__pts-bar" aria-hidden="true"></span>20</span></li>
					<li class="ds-infographic__rank-item"><span class="ds-infographic__place">2</span><span>Скетчинг</span><span class="ds-infographic__pts" style="--p: 16"><span class="ds-infographic__pts-bar" aria-hidden="true"></span>16</span></li>
				</ol>
			</div>
			<div class="ds-infographic__list ds-infographic__list--risk">
				<p class="ds-infographic__list-title">Высокий риск</p>
				<ol class="ds-infographic__rank">
					<li class="ds-infographic__rank-item"><span class="ds-infographic__place">43</span><span>Персоны</span><span class="ds-infographic__pts" style="--p: 8"><span class="ds-infographic__pts-bar" aria-hidden="true"></span>8</span></li>
				</ol>
			</div>
		</div>
		<p class="ds-infographic__source">Jakob Nielsen, 16.09.2026</p>
	</figure>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Схема «было → стало»</figcaption>
		<div class="ds-infographic__scheme">
			<div class="ds-infographic__scheme-col">
				<span class="ds-infographic__scheme-head">Было</span>
				<div class="ds-infographic__levels"><span class="ds-infographic__level">A</span><span class="ds-infographic__level">AA</span><span class="ds-infographic__level ds-infographic__level--off">AAA</span></div>
			</div>
			<span class="ds-infographic__arrow" aria-hidden="true">→</span>
			<div class="ds-infographic__scheme-col">
				<span class="ds-infographic__scheme-head">Стало</span>
				<div class="ds-infographic__box ds-infographic__box--core"><b>Основное</b><span class="ds-infographic__box-note">на&nbsp;уровнях A и&nbsp;AA</span></div>
				<div class="ds-infographic__box ds-infographic__box--extra"><b>Дополнительное</b><span class="ds-infographic__box-note">то, что подходит не&nbsp;везде</span></div>
				<div class="ds-infographic__box ds-infographic__box--tag"><b>Метка</b><span class="ds-infographic__box-note">пунктир&nbsp;— необязательное</span></div>
			</div>
		</div>
		<p class="ds-infographic__source">W3C, блог, 25.09.2026</p>
	</figure>

	<figure class="ds-infographic">
		<figcaption class="ds-infographic__title">Механика</figcaption>
		<div class="ds-infographic__mech">
			<div class="ds-infographic__mech-case ds-infographic__mech-case--over">
				<p class="ds-infographic__mech-text">Без переноса 5–6 вылезают за&nbsp;фрейм.</p>
				<div class="ds-infographic__frame ds-infographic__frame--over">
					<div class="ds-infographic__items"><span class="ds-infographic__item">1</span><span class="ds-infographic__item">2</span><span class="ds-infographic__item">3</span><span class="ds-infographic__item">4</span><span class="ds-infographic__item ds-infographic__item--out">5</span><span class="ds-infographic__item ds-infographic__item--out">6</span></div>
					<span class="ds-infographic__cut" aria-hidden="true"></span>
				</div>
			</div>
			<div class="ds-infographic__mech-case">
				<p class="ds-infographic__mech-text">С&nbsp;переносом 5–6 во&nbsp;второй колонке.</p>
				<div class="ds-infographic__frame ds-infographic__frame--wrap">
					<div class="ds-infographic__items"><span class="ds-infographic__item">1</span><span class="ds-infographic__item">2</span><span class="ds-infographic__item">3</span><span class="ds-infographic__item">4</span><span class="ds-infographic__item">5</span><span class="ds-infographic__item">6</span></div>
				</div>
			</div>
		</div>
		<p class="ds-infographic__source">Figma, release notes, 25.09.2026</p>
	</figure>
</div>
<!-- /wp:html -->
