import { Text } from "./text";

export const Logo = () => {
  return (
    <div className="h-32 flex flex-row gap-2 items-center">
      <img src="/DocMcQueryTransparent.png" className="h-32" />
      <div className="flex flex-col -top-4">
        <Text size="t1" className="leading-none">
          Doc McQuery
        </Text>
        <Text size="t2" className="-top-5">
          Smarter searches, better care.
        </Text>
      </div>
    </div>
  );
};
