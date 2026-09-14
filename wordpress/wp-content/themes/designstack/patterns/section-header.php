<?php
/**
 * Title: Заголовок блока
 * Slug: designstack/section-header
 * Categories: designstack
 *
 * Три варианта: простой, со строкой под заголовком и со ссылкой «все». От 900 ссылка стоит справа от заголовка,
 * ниже — под содержимым блока. Над заголовком воздуха вдвое больше, чем под ним (D50).
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<section class="ds-section">
		<div class="ds-section__head"><h2 class="ds-section__title">Новое в каталоге</h2></div>
		<div class="ds-section__body"><p class="ds-meta">здесь стоит список ресурсов</p></div>
	</section>
	<section class="ds-section">
		<div class="ds-section__head">
			<h2 class="ds-section__title">Проверено на этой неделе</h2>
			<p class="ds-section__sub">Эти записи мы пересмотрели за последнюю неделю</p>
		</div>
		<div class="ds-section__body"><p class="ds-meta">здесь стоит список ресурсов</p></div>
	</section>
	<section class="ds-section">
		<div class="ds-section__head"><h2 class="ds-section__title">Свежие подборки</h2></div>
		<div class="ds-section__body"><p class="ds-meta">здесь стоят карточки подборок</p></div>
		<div class="ds-section__more"><a class="ds-link ds-link--standalone" href="/collections/">Все подборки<?php echo designstack_icon( 'chevron-right' ); ?></a></div>
	</section>
</div>
<!-- /wp:html -->
