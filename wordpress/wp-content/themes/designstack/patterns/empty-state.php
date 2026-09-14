<?php
/**
 * Title: Пустые состояния
 * Slug: designstack/empty-state
 * Categories: designstack
 * Inserter: no
 *
 * Причина словами и что сделать (US-19, US-21, US-23). Иллюстрация — линия на токенах, один акцентный предмет (D50 §8).
 * На странице 404 заголовок этого блока становится h1 — это делает шаблон этапа 13.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<section class="ds-empty ds-empty--filters">
		<?php echo designstack_illustration( 'empty-filters' ); ?>
		<h2 class="ds-empty__title">По таким условиям ничего нет</h2>
		<p class="ds-empty__text">Российских инструментов для прототипирования в каталоге пока нет. Попробуй снять фильтр «Российский».</p>
		<div class="ds-empty__actions">
			<a class="ds-button ds-button--primary" href="/tools/">Сбросить фильтры</a>
			<a class="ds-link" href="/suggest/">Предложить ресурс</a>
		</div>
	</section>
	<section class="ds-empty ds-empty--section">
		<?php echo designstack_illustration( 'empty-section' ); ?>
		<h2 class="ds-empty__title">В разделе пока нет ресурсов</h2>
		<div class="ds-empty__actions"><a class="ds-link" href="/suggest/">Предложить ресурс</a></div>
	</section>
	<section class="ds-empty ds-empty--search">
		<?php echo designstack_illustration( 'empty-filters' ); ?>
		<h2 class="ds-empty__title">По запросу «экслидроу» ничего нет</h2>
		<p class="ds-empty__text">Попробуй короче или другими словами. Если ресурса нет в каталоге — предложи его.</p>
		<div class="ds-empty__actions"><a class="ds-link" href="/suggest/">Предложить ресурс</a></div>
	</section>
	<section class="ds-empty ds-empty--not-found">
		<?php echo designstack_illustration( 'not-found' ); ?>
		<h2 class="ds-empty__title">Такой страницы нет</h2>
		<p class="ds-empty__text">Адрес мог измениться или в нём опечатка. Найди ресурс поиском или открой раздел.</p>
	</section>
</div>
<!-- /wp:html -->
